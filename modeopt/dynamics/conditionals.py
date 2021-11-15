#!/usr/bin/env python3

# Copyright 2017-2020 The GPflow Contributors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional

import tensorflow as tf
from gpflow import covariances, mean_functions
from gpflow.config import default_float, default_jitter
from gpflow.expectations import expectation
from gpflow.inducing_variables import InducingVariables
from gpflow.kernels import Kernel
from gpflow.probability_distributions import Gaussian


# class FakeInducingPoints(InducingPoints):
class FakeInducingPoints(InducingVariables):
    def __init__(self, Z, name: Optional[str] = None):
        """
        :param Z: the initial positions of the inducing points, size [M, D]
        """
        super().__init__(name=name)
        # if not isinstance(Z, (tf.Variable, tfp.util.TransformedVariable)):
        #     Z = Parameter(Z)
        self.Z = Z

    def __len__(self) -> int:
        return tf.shape(self.Z)[0]


def uncertain_conditional(
    Xnew_mu: tf.Tensor,
    Xnew_var: tf.Tensor,
    inducing_variable: InducingVariables,
    kernel: Kernel,
    q_mu,
    q_sqrt,
    *,
    mean_function=None,
    full_output_cov=False,
    full_cov=False,
    white=False,
):
    """
    Calculates the conditional for uncertain inputs Xnew, p(Xnew) = N(Xnew_mu, Xnew_var).
    See ``conditional`` documentation for further reference.
    :param Xnew_mu: mean of the inputs, size [N, D]in
    :param Xnew_var: covariance matrix of the inputs, size [N, n, n]
    :param inducing_variable: gpflow.InducingVariable object, only InducingPoints is supported
    :param kernel: gpflow kernel object.
    :param q_mu: mean inducing points, size [M, Dout]
    :param q_sqrt: cholesky of the covariance matrix of the inducing points, size [t, M, M]
    :param full_output_cov: boolean wheter to compute covariance between output dimension.
                            Influences the shape of return value ``fvar``. Default is False
    :param white: boolean whether to use whitened representation. Default is False.
    :return fmean, fvar: mean and covariance of the conditional, size ``fmean`` is [N, Dout],
            size ``fvar`` depends on ``full_output_cov``: if True ``f_var`` is [N, t, t],
            if False then ``f_var`` is [N, Dout]
    """

    # if not isinstance(inducing_variable, InducingPoints):
    #     raise NotImplementedError

    if full_cov:
        raise NotImplementedError(
            "uncertain_conditional() currently does not support full_cov=True"
        )

    pXnew = Gaussian(Xnew_mu, Xnew_var)

    num_data = tf.shape(Xnew_mu)[0]  # number of new inputs (N)
    num_ind, num_func = tf.unstack(
        tf.shape(q_mu), num=2, axis=0
    )  # number of inducing points (M), output dimension (D)
    q_sqrt_r = tf.linalg.band_part(q_sqrt, -1, 0)  # [D, M, M]

    eKuf = tf.transpose(
        expectation(pXnew, (kernel, inducing_variable))
    )  # [M, N] (psi1)
    Kuu = covariances.Kuu(inducing_variable, kernel, jitter=default_jitter())  # [M, M]
    Luu = tf.linalg.cholesky(Kuu)  # [M, M]

    if not white:
        q_mu = tf.linalg.triangular_solve(Luu, q_mu, lower=True)
        Luu_tiled = tf.tile(
            Luu[None, :, :], [num_func, 1, 1]
        )  # remove line once issue 216 is fixed
        q_sqrt_r = tf.linalg.triangular_solve(Luu_tiled, q_sqrt_r, lower=True)

    Li_eKuf = tf.linalg.triangular_solve(Luu, eKuf, lower=True)  # [M, N]
    fmean = tf.linalg.matmul(Li_eKuf, q_mu, transpose_a=True)

    eKff = expectation(pXnew, kernel)  # N (psi0)
    eKuffu = expectation(
        pXnew, (kernel, inducing_variable), (kernel, inducing_variable)
    )  # [N, M, M] (psi2)
    Luu_tiled = tf.tile(
        Luu[None, :, :], [num_data, 1, 1]
    )  # remove this line, once issue 216 is fixed
    Li_eKuffu = tf.linalg.triangular_solve(Luu_tiled, eKuffu, lower=True)
    Li_eKuffu_Lit = tf.linalg.triangular_solve(
        Luu_tiled, tf.linalg.adjoint(Li_eKuffu), lower=True
    )  # [N, M, M]
    cov = tf.linalg.matmul(q_sqrt_r, q_sqrt_r, transpose_b=True)  # [D, M, M]

    if mean_function is None or isinstance(mean_function, mean_functions.Zero):
        e_related_to_mean = tf.zeros(
            (num_data, num_func, num_func), dtype=default_float()
        )
    else:
        # Update mean: \mu(x) + m(x)
        fmean = fmean + expectation(pXnew, mean_function)

        # Calculate: m(x) m(x)^T + m(x) \mu(x)^T + \mu(x) m(x)^T,
        # where m(x) is the mean_function and \mu(x) is fmean
        e_mean_mean = expectation(pXnew, mean_function, mean_function)  # [N, D, D]
        Lit_q_mu = tf.linalg.triangular_solve(Luu, q_mu, adjoint=True)
        e_mean_Kuf = expectation(
            pXnew, mean_function, (kernel, inducing_variable)
        )  # [N, D, M]
        # einsum isn't able to infer the rank of e_mean_Kuf, hence we explicitly set the rank of the tensor:
        e_mean_Kuf = tf.reshape(e_mean_Kuf, [num_data, num_func, num_ind])
        e_fmean_mean = tf.einsum("nqm,mz->nqz", e_mean_Kuf, Lit_q_mu)  # [N, D, D]
        e_related_to_mean = e_fmean_mean + tf.linalg.adjoint(e_fmean_mean) + e_mean_mean

    if full_output_cov:
        fvar = (
            tf.linalg.diag(
                tf.tile((eKff - tf.linalg.trace(Li_eKuffu_Lit))[:, None], [1, num_func])
            )
            + tf.linalg.diag(tf.einsum("nij,dji->nd", Li_eKuffu_Lit, cov))
            +
            # tf.linalg.diag(tf.linalg.trace(tf.linalg.matmul(Li_eKuffu_Lit, cov))) +
            tf.einsum("ig,nij,jh->ngh", q_mu, Li_eKuffu_Lit, q_mu)
            -
            # tf.linalg.matmul(q_mu, tf.linalg.matmul(Li_eKuffu_Lit, q_mu), transpose_a=True) -
            fmean[:, :, None] * fmean[:, None, :]
            + e_related_to_mean
        )
    else:
        fvar = (
            (eKff - tf.linalg.trace(Li_eKuffu_Lit))[:, None]
            + tf.einsum("nij,dji->nd", Li_eKuffu_Lit, cov)
            + tf.einsum("ig,nij,jg->ng", q_mu, Li_eKuffu_Lit, q_mu)
            - fmean ** 2
            + tf.linalg.diag_part(e_related_to_mean)
        )

    return fmean, fvar


def svgp_covariance_conditional(X1, X2, svgp):
    return covariance_conditional(
        X1,
        X2,
        kernel=svgp.kernel,
        inducing_variable=svgp.inducing_variable,
        f=svgp.q_mu,
        q_sqrt=svgp.q_sqrt,
        white=svgp.whiten,
    )


def covariance_conditional(
    X1, X2, kernel, inducing_variable, f, q_sqrt=None, white=False
):
    K12 = kernel(X1, X2)
    # print("K12")
    # print(K12.shape)
    Kmm = kernel(inducing_variable.Z, inducing_variable.Z)
    # print("Kmm")
    # print(Kmm.shape)
    Lm = tf.linalg.cholesky(Kmm)
    # print("Lm")
    # print(Lm.shape)

    Km1 = kernel(inducing_variable.Z, X1)
    Km2 = kernel(inducing_variable.Z, X2)
    # print("Km1.shape")
    # print(Km1.shape)
    # print(Km2.shape)
    return base_covariance_conditional(
        Km1=Km1,
        Km2=Km2,
        Lm=Lm,
        K12=K12,
        f=f,
        q_sqrt=q_sqrt,
        white=white,
        # X1,
        # X2,
        # kernel=svgp.kernel,
        # inducing_variable=svgp.inducing_variable,
        # q_mu=svgp.q_mu,
        # q_sqrt=svgp.q_sqrt,
    )


def base_covariance_conditional(
    Km1: tf.Tensor,
    Km2: tf.Tensor,
    Lm: tf.Tensor,
    K12: tf.Tensor,
    f: tf.Tensor,
    *,
    # full_cov=False,
    q_sqrt: Optional[tf.Tensor] = None,
    white=False,
):
    # compute kernel stuff
    num_func = tf.shape(f)[-1]  # R
    N1 = tf.shape(Km1)[-1]
    N2 = tf.shape(Km2)[-1]
    M = tf.shape(f)[-2]

    # get the leading dims in Kmn to the front of the tensor
    # if Kmn has rank two, i.e. [M, N], this is the identity op.
    K1 = tf.rank(Km1)
    K2 = tf.rank(Km2)
    perm_1 = tf.concat(
        [
            tf.reshape(tf.range(1, K1 - 1), [K1 - 2]),  # leading dims (...)
            tf.reshape(0, [1]),  # [M]
            tf.reshape(K1 - 1, [1]),
        ],
        0,
    )  # [N]
    perm_2 = tf.concat(
        [
            tf.reshape(tf.range(1, K2 - 1), [K2 - 2]),  # leading dims (...)
            tf.reshape(0, [1]),  # [M]
            tf.reshape(K2 - 1, [1]),
        ],
        0,
    )  # [N]
    Km1 = tf.transpose(Km1, perm_1)  # [..., M, N1]
    Km2 = tf.transpose(Km2, perm_2)  # [..., M, N2]
    # print("Km1")
    # print(Km1.shape)
    # print(Km2.shape)

    shape_constraints = [
        (Km1, [..., "M", "N1"]),
        (Km2, [..., "M", "N2"]),
        (Lm, ["M", "M"]),
        (K12, [..., "N1", "N2"]),
        (f, ["M", "R"]),
    ]
    if q_sqrt is not None:
        shape_constraints.append(
            (q_sqrt, (["M", "R"] if q_sqrt.shape.ndims == 2 else ["R", "M", "M"]))
        )
    tf.debugging.assert_shapes(
        shape_constraints,
        message="base_conditional() arguments "
        "[Note that this check verifies the shape of an alternative "
        "representation of Kmn. See the docs for the actual expected "
        "shape.]",
    )

    leading_dims = tf.shape(Km1)[:-2]

    # Compute the projection matrix A
    Lm = tf.broadcast_to(Lm, tf.concat([leading_dims, tf.shape(Lm)], 0))  # [..., M, M]
    # print("Lm")
    # print(Lm.shape)
    A1 = tf.linalg.triangular_solve(Lm, Km1, lower=True)  # [..., M, N1]
    print("A1")
    print(A1.shape)
    A2 = tf.linalg.triangular_solve(Lm, Km2, lower=True)  # [..., M, N2]
    print("A2")
    print(A2.shape)

    # compute the covariance due to the conditioning
    fcov = K12 - tf.linalg.matmul(A1, A2, transpose_a=True)  # [..., N1, N2]
    # if not full_cov:
    #     fcov = tf.linalg.diag_part(fcov)
    cov_shape = tf.concat([leading_dims, [num_func, N1, N2]], 0)
    fcov = tf.broadcast_to(tf.expand_dims(fcov, -3), cov_shape)  # [..., R, N1, N2]

    # another backsubstitution in the unwhitened case
    # TODO what if white=False?
    # if not white:
    #     A = tf.linalg.triangular_solve(tf.linalg.adjoint(Lm), A, lower=False)

    if q_sqrt is not None:
        q_sqrt_dims = q_sqrt.shape.ndims
        if q_sqrt_dims == 2:
            LTA1 = A1 * tf.expand_dims(tf.transpose(q_sqrt), 2)  # [R, M, N1]
            LTA2 = A2 * tf.expand_dims(tf.transpose(q_sqrt), 2)  # [R, M, N2]
        elif q_sqrt_dims == 3:
            L = tf.linalg.band_part(q_sqrt, -1, 0)  # force lower triangle # [R, M, M]
            L_shape = tf.shape(L)
            L = tf.broadcast_to(L, tf.concat([leading_dims, L_shape], 0))

            shape1 = tf.concat([leading_dims, [num_func, M, N1]], axis=0)
            shape2 = tf.concat([leading_dims, [num_func, M, N2]], axis=0)
            A1_tiled = tf.broadcast_to(tf.expand_dims(A1, -3), shape1)
            A2_tiled = tf.broadcast_to(tf.expand_dims(A2, -3), shape2)
            LTA1 = tf.linalg.matmul(L, A1_tiled, transpose_a=True)  # [R, M, N1]
            LTA2 = tf.linalg.matmul(L, A2_tiled, transpose_a=True)  # [R, M, N2]
        else:  # pragma: no cover
            raise ValueError("Bad dimension for q_sqrt: %s" % str(q_sqrt.shape.ndims))
        print("LTA1")
        print(LTA1.shape)
        print(LTA2.shape)

        # fcov = fcov + tf.linalg.matmul(LTA, LTA, transpose_a=True)  # [R, N, N]
        fcov = fcov + tf.linalg.matmul(LTA1, LTA2, transpose_a=True)  # [R, N1, N2]

    # if not full_cov:
    #     fcov = tf.linalg.adjoint(fcov)  # [N, R]

    # shape_constraints = [
    #     (Km1, [..., "M", "N1"]),  # tensor included again for N dimension
    #     (f, [..., "M", "R"]),  # tensor included again for R dimension
    #     (fmean, [..., "N", "R"]),
    #     (fvar, [..., "R", "N1", "N2"] if full_cov else [..., "N1", "R"]),
    # ]
    # tf.debugging.assert_shapes(
    #     shape_constraints, message="base_conditional() return values"
    # )

    # return fmean, fvar
    return fcov


def base_svgp_conditional(X1, X2, kernel, inducing_variable, q_mu, q_sqrt):
    K12 = kernel(X1, X2)
    print("K12")
    print(K12.shape)
    Kzz = kernel(inducing_variable.Z, inducing_variable.Z)
    # jitter=1e-6
    jitter = 1e-4
    Kzz += jitter * tf.eye(inducing_variable.num_inducing, dtype=Kzz.dtype)
    print("Kzz")
    print(Kzz.shape)
    Lz = tf.linalg.cholesky(Kzz)
    print("Lz")
    print(Lz.shape)

    K1z = kernel(X1, inducing_variable.Z)
    # Kz2 = kernel(X2, inducing_variable.Z)
    Kz2 = kernel(inducing_variable.Z, X2)
    print("K1z.shape")
    print(K1z.shape)
    print(Kz2.shape)

    S = q_sqrt @ tf.transpose(q_sqrt, [0, 2, 1])
    A = Kzz - S[0, :, :]
    print("A.shape")
    print(A.shape)
    # B = Kz1 @ A @ tf.transpose(Kz2)
    B = K1z @ A @ Kz2
    print("B.shape")
    print(B.shape)
    K = K12 - B
    print("K.shape")
    print(K.shape)
    return K

    # # Compute the projection matrix A
    # Lm = tf.broadcast_to(Lm, tf.concat([leading_dims, tf.shape(Lm)], 0))  # [..., M, M]
    # A = tf.linalg.triangular_solve(Lm, Kmn, lower=True)  # [..., M, N]


# def split_base_conditional_with_lm(
#     K1m: tf.Tensor,
#     Km2: tf.Tensor,
#     K12: tf.Tensor,
#     Lm: tf.Tensor,
#     f: tf.Tensor,
#     *,
#     full_cov=False,
#     q_sqrt: Optional[tf.Tensor] = None,
#     white=False,
# ):
#     # compute kernel stuff
#     num_func = tf.shape(f)[-1]  # R
#     N1 = tf.shape(K1m)[-2]
#     N2 = tf.shape(Km2)[-1]
#     M = tf.shape(f)[-2]

#     # get the leading dims in Kmn to the front of the tensor
#     # if Kmn has rank two, i.e. [M, N], this is the identity op.
#     K2 = tf.rank(Km2)
#     perm_2 = tf.concat(
#         [
#             tf.reshape(tf.range(1, K2 - 1), [K2 - 2]),  # leading dims (...)
#             tf.reshape(0, [1]),  # [M]
#             tf.reshape(K2 - 1, [1]),
#         ],
#         0,
#     )  # [N]
#     Kmn = tf.transpose(Kmn, perm)  # [..., M, N]

#     shape_constraints = [
#         (K1m, [..., "N1", "M"]),
#         (Km2, [..., "M", "N2"]),
#         (Lm, ["M", "M"]),
#         (K12, [..., "N1", "N2"] if full_cov else [..., "N1"]),
#         (f, ["M", "R"]),
#     ]
#     if q_sqrt is not None:
#         shape_constraints.append(
#             (q_sqrt, (["M", "R"] if q_sqrt.shape.ndims == 2 else ["R", "M", "M"]))
#         )
#     tf.debugging.assert_shapes(
#         shape_constraints,
#         message="base_conditional() arguments "
#         "[Note that this check verifies the shape of an alternative "
#         "representation of Kmn. See the docs for the actual expected "
#         "shape.]",
#     )

#     leading_dims = tf.shape(Kmn)[:-2]

#     # Compute the projection matrix A
#     Lm = tf.broadcast_to(Lm, tf.concat([leading_dims, tf.shape(Lm)], 0))  # [..., M, M]
#     A = tf.linalg.triangular_solve(Lm, Kmn, lower=True)  # [..., M, N]

#     K12 = kernel(X1, X2)
#     print("K12")
#     print(K12.shape)
#     Kzz = kernel(inducing_variable.Z, inducing_variable.Z)
#     print("Kzz")
#     print(Kzz.shape)
#     Lz = tf.linalg.cholesky(Kzz)
#     print("Lz")
#     print(Lz.shape)

#     K1z = kernel(X1, inducing_variable.Z)
#     # Kz2 = kernel(X2, inducing_variable.Z)
#     Kz2 = kernel(inducing_variable.Z, X2)
#     print("K1z.shape")
#     print(K1z.shape)
#     print(Kz2.shape)

#     S = q_sqrt @ tf.transpose(q_sqrt, [0, 2, 1])
#     A = Kzz - S[0, :, :]
#     print("A.shape")
#     print(A.shape)
#     # B = Kz1 @ A @ tf.transpose(Kz2)
#     B = K1z @ A @ Kz2
#     print("B.shape")
#     print(B.shape)
#     K = K12 - B
#     print("K.shape")
#     print(K.shape)
#     return K

#     # # Compute the projection matrix A
#     # Lm = tf.broadcast_to(Lm, tf.concat([leading_dims, tf.shape(Lm)], 0))  # [..., M, M]
#     # A = tf.linalg.triangular_solve(Lm, Kmn, lower=True)  # [..., M, N]


# def svgp_conditional_split(X1,X2,svgp):
#     Km1


def base_conditional_split(
    Km1: tf.Tensor,
    Km2: tf.Tensor,
    Kmm: tf.Tensor,
    Knn: tf.Tensor,
    f: tf.Tensor,
    *,
    full_cov=False,
    q_sqrt: Optional[tf.Tensor] = None,
    white=False,
):
    Lm = tf.linalg.cholesky(Kmm)
    return base_conditional_with_lm(
        Km1, Km2, Lm, Knn, f=f, full_cov=full_cov, q_sqrt=q_sqrt, white=white
    )
