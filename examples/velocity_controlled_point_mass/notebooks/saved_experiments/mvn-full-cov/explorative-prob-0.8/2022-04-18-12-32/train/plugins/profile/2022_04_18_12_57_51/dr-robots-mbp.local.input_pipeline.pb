  *	     8?@2e
.Iterator::Root::ParallelMapV2::Zip[0]::FlatMap
ףp=
??!D?JԮDM@)??S㥛??1.????-J@:Preprocessing2?
KIterator::Root::ParallelMapV2::Zip[0]::FlatMap::Prefetch::Map::FiniteRepeat??ʡE???!??h
9@)333333??1dp>?c8@:Preprocessing2t
=Iterator::Root::ParallelMapV2::Zip[0]::FlatMap::Prefetch::Map?$??C??!Q??+QA@)h??|?5??10????/#@:Preprocessing2v
?Iterator::Root::ParallelMapV2::Zip[0]::FlatMap[16]::ConcatenateV-???!???-??@)???S㥛?1?????@:Preprocessing2k
4Iterator::Root::ParallelMapV2::Zip[1]::ForeverRepeat????Mb??!?M!?@)???Q???1??18?@:Preprocessing2T
Iterator::Root::ParallelMapV2y?&1???!6?a#6@)y?&1???16?a#6@:Preprocessing2E
Iterator::Root?~j?t???!8??18@){?G?z??1?B?)??:Preprocessing2o
8Iterator::Root::ParallelMapV2::Zip[0]::FlatMap::Prefetch;?O??n??!kW?v%j??);?O??n??1kW?v%j??:Preprocessing2?
RIterator::Root::ParallelMapV2::Zip[0]::FlatMap::Prefetch::Map::FiniteRepeat::Range????Mbp?!?M!???)????Mbp?1?M!???:Preprocessing2?
NIterator::Root::ParallelMapV2::Zip[0]::FlatMap[16]::Concatenate[1]::FromTensor????Mb`?!?M!???)????Mb`?1?M!???:Preprocessing2?
OIterator::Root::ParallelMapV2::Zip[0]::FlatMap[17]::Concatenate[0]::TensorSlice????MbP?!?M!???)????MbP?1?M!???:Preprocessing2?
NIterator::Root::ParallelMapV2::Zip[0]::FlatMap[17]::Concatenate[1]::FromTensor????MbP?!?M!???)????MbP?1?M!???:Preprocessing2w
@Iterator::Root::ParallelMapV2::Zip[1]::ForeverRepeat::FromTensor????MbP?!?M!???)????MbP?1?M!???:Preprocessing:?
]Enqueuing data: you may want to combine small input data chunks into fewer but larger chunks.
?Data preprocessing: you may increase num_parallel_calls in <a href="https://www.tensorflow.org/api_docs/python/tf/data/Dataset#map" target="_blank">Dataset map()</a> or preprocess the data OFFLINE.
?Reading data from files in advance: you may tune parameters in the following tf.data API (<a href="https://www.tensorflow.org/api_docs/python/tf/data/Dataset#prefetch" target="_blank">prefetch size</a>, <a href="https://www.tensorflow.org/api_docs/python/tf/data/Dataset#interleave" target="_blank">interleave cycle_length</a>, <a href="https://www.tensorflow.org/api_docs/python/tf/data/TFRecordDataset#class_tfrecorddataset" target="_blank">reader buffer_size</a>)
?Reading data from files on demand: you should read data IN ADVANCE using the following tf.data API (<a href="https://www.tensorflow.org/api_docs/python/tf/data/Dataset#prefetch" target="_blank">prefetch</a>, <a href="https://www.tensorflow.org/api_docs/python/tf/data/Dataset#interleave" target="_blank">interleave</a>, <a href="https://www.tensorflow.org/api_docs/python/tf/data/TFRecordDataset#class_tfrecorddataset" target="_blank">reader buffer</a>)
?Other data reading or processing: you may consider using the <a href="https://www.tensorflow.org/programmers_guide/datasets" target="_blank">tf.data API</a> (if you are not using it now)?
:type.googleapis.com/tensorflow.profiler.BottleneckAnalysisk
unknownTNo step time measured. Therefore we cannot tell where the performance bottleneck is.no*noZno#You may skip the rest of this page.BZ
@type.googleapis.com/tensorflow.profiler.GenericStepTimeBreakdown
  " * 2 : B J R Z b JCPU_ONLYb??No step marker observed and hence the step time is unknown. This may happen if (1) training steps are not instrumented (e.g., if you are not using Keras) or (2) the profiling duration is shorter than the step time. For (1), you need to add step instrumentation; for (2), you may try to profile longer.