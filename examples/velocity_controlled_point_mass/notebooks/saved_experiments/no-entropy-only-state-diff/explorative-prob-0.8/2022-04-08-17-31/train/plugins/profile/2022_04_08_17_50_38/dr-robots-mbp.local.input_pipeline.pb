  *	     ?@2t
=Iterator::Root::ParallelMapV2::Zip[0]::FlatMap::Prefetch::Map??ʡE@!h?????G@)%??C?@1?HB}6?E@:Preprocessing2e
.Iterator::Root::ParallelMapV2::Zip[0]::FlatMap-???????!?p?)<@)?l??????1G???J9@:Preprocessing2T
Iterator::Root::ParallelMapV2u?V??!?(?m?`7@)u?V??1?(?m?`7@:Preprocessing2?
KIterator::Root::ParallelMapV2::Zip[0]::FlatMap::Prefetch::Map::FiniteRepeat???S????!J??w?@)??n????1ή? @:Preprocessing2v
?Iterator::Root::ParallelMapV2::Zip[0]::FlatMap[16]::Concatenate???Q???!????
&??)X9??v??1??E?????:Preprocessing2v
?Iterator::Root::ParallelMapV2::Zip[0]::FlatMap[17]::Concatenate??~j?t??!GD?$:???)?? ?rh??1??'П???:Preprocessing2k
4Iterator::Root::ParallelMapV2::Zip[1]::ForeverRepeat??~j?t??!GD?$:???)X9??v???1?Ҝ???:Preprocessing2E
Iterator::Root/?$???!??W0??7@)y?&1???1?#?p??:Preprocessing2o
8Iterator::Root::ParallelMapV2::Zip[0]::FlatMap::Prefetch??~j?t??!GD?$:???)??~j?t??1GD?$:???:Preprocessing2Y
"Iterator::Root::ParallelMapV2::Zip?~j?t???!I?*f??<@)?~j?t???1	°?;???:Preprocessing2?
RIterator::Root::ParallelMapV2::Zip[0]::FlatMap::Prefetch::Map::FiniteRepeat::Rangey?&1?|?!?#?p??)y?&1?|?1?#?p??:Preprocessing2w
@Iterator::Root::ParallelMapV2::Zip[1]::ForeverRepeat::FromTensory?&1?|?!?#?p??)y?&1?|?1?#?p??:Preprocessing2?
OIterator::Root::ParallelMapV2::Zip[0]::FlatMap[17]::Concatenate[0]::TensorSlice????Mb`?!,˥Ҝ??)????Mb`?1,˥Ҝ??:Preprocessing2?
NIterator::Root::ParallelMapV2::Zip[0]::FlatMap[17]::Concatenate[1]::FromTensor????Mb`?!,˥Ҝ??)????Mb`?1,˥Ҝ??:Preprocessing2?
NIterator::Root::ParallelMapV2::Zip[0]::FlatMap[16]::Concatenate[1]::FromTensor????MbP?!,˥Ҝ??)????MbP?1,˥Ҝ??:Preprocessing:?
]Enqueuing data: you may want to combine small input data chunks into fewer but larger chunks.
?Data preprocessing: you may increase num_parallel_calls in <a href="https://www.tensorflow.org/api_docs/python/tf/data/Dataset#map" target="_blank">Dataset map()</a> or preprocess the data OFFLINE.
?Reading data from files in advance: you may tune parameters in the following tf.data API (<a href="https://www.tensorflow.org/api_docs/python/tf/data/Dataset#prefetch" target="_blank">prefetch size</a>, <a href="https://www.tensorflow.org/api_docs/python/tf/data/Dataset#interleave" target="_blank">interleave cycle_length</a>, <a href="https://www.tensorflow.org/api_docs/python/tf/data/TFRecordDataset#class_tfrecorddataset" target="_blank">reader buffer_size</a>)
?Reading data from files on demand: you should read data IN ADVANCE using the following tf.data API (<a href="https://www.tensorflow.org/api_docs/python/tf/data/Dataset#prefetch" target="_blank">prefetch</a>, <a href="https://www.tensorflow.org/api_docs/python/tf/data/Dataset#interleave" target="_blank">interleave</a>, <a href="https://www.tensorflow.org/api_docs/python/tf/data/TFRecordDataset#class_tfrecorddataset" target="_blank">reader buffer</a>)
?Other data reading or processing: you may consider using the <a href="https://www.tensorflow.org/programmers_guide/datasets" target="_blank">tf.data API</a> (if you are not using it now)?
:type.googleapis.com/tensorflow.profiler.BottleneckAnalysisk
unknownTNo step time measured. Therefore we cannot tell where the performance bottleneck is.no*noZno#You may skip the rest of this page.BZ
@type.googleapis.com/tensorflow.profiler.GenericStepTimeBreakdown
  " * 2 : B J R Z b JCPU_ONLYb??No step marker observed and hence the step time is unknown. This may happen if (1) training steps are not instrumented (e.g., if you are not using Keras) or (2) the profiling duration is shorter than the step time. For (1), you need to add step instrumentation; for (2), you may try to profile longer.