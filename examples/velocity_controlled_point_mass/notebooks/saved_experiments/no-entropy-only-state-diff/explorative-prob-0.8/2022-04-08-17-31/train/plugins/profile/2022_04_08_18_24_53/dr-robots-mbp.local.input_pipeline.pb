  *	      ?@2e
.Iterator::Root::ParallelMapV2::Zip[0]::FlatMap????????!?$I?$?N@)??C?l???1I?$I?TH@:Preprocessing2t
=Iterator::Root::ParallelMapV2::Zip[0]::FlatMap::Prefetch::Map?A`??"??!?m۶m?@@)?(\?????1?m۶m?=@:Preprocessing2v
?Iterator::Root::ParallelMapV2::Zip[0]::FlatMap[16]::Concatenate??|?5^??!۶m۶?&@)?&1???1I?$I??&@:Preprocessing2?
KIterator::Root::ParallelMapV2::Zip[0]::FlatMap::Prefetch::Map::FiniteRepeat?? ?rh??!?m۶m[@)???Q???1?$I?$?
@:Preprocessing2T
Iterator::Root::ParallelMapV2?? ?rh??!?m۶m[??)?? ?rh??1?m۶m[??:Preprocessing2k
4Iterator::Root::ParallelMapV2::Zip[1]::ForeverRepeat?? ?rh??!?m۶m[??)9??v????1n۶m?6??:Preprocessing2o
8Iterator::Root::ParallelMapV2::Zip[0]::FlatMap::Prefetch?I+???!I?$I????)?I+???1I?$I????:Preprocessing2E
Iterator::Root???S㥛?!?m۶m@){?G?z??1?m۶m???:Preprocessing2?
RIterator::Root::ParallelMapV2::Zip[0]::FlatMap::Prefetch::Map::FiniteRepeat::Range????Mbp?!$I?$I???)????Mbp?1$I?$I???:Preprocessing2w
@Iterator::Root::ParallelMapV2::Zip[1]::ForeverRepeat::FromTensor????Mbp?!$I?$I???)????Mbp?1$I?$I???:Preprocessing2?
NIterator::Root::ParallelMapV2::Zip[0]::FlatMap[17]::Concatenate[1]::FromTensor????Mb`?!$I?$I???)????Mb`?1$I?$I???:Preprocessing2?
NIterator::Root::ParallelMapV2::Zip[0]::FlatMap[16]::Concatenate[1]::FromTensor????MbP?!$I?$I???)????MbP?1$I?$I???:Preprocessing2?
OIterator::Root::ParallelMapV2::Zip[0]::FlatMap[17]::Concatenate[0]::TensorSlice????MbP?!$I?$I???)????MbP?1$I?$I???:Preprocessing:?
]Enqueuing data: you may want to combine small input data chunks into fewer but larger chunks.
?Data preprocessing: you may increase num_parallel_calls in <a href="https://www.tensorflow.org/api_docs/python/tf/data/Dataset#map" target="_blank">Dataset map()</a> or preprocess the data OFFLINE.
?Reading data from files in advance: you may tune parameters in the following tf.data API (<a href="https://www.tensorflow.org/api_docs/python/tf/data/Dataset#prefetch" target="_blank">prefetch size</a>, <a href="https://www.tensorflow.org/api_docs/python/tf/data/Dataset#interleave" target="_blank">interleave cycle_length</a>, <a href="https://www.tensorflow.org/api_docs/python/tf/data/TFRecordDataset#class_tfrecorddataset" target="_blank">reader buffer_size</a>)
?Reading data from files on demand: you should read data IN ADVANCE using the following tf.data API (<a href="https://www.tensorflow.org/api_docs/python/tf/data/Dataset#prefetch" target="_blank">prefetch</a>, <a href="https://www.tensorflow.org/api_docs/python/tf/data/Dataset#interleave" target="_blank">interleave</a>, <a href="https://www.tensorflow.org/api_docs/python/tf/data/TFRecordDataset#class_tfrecorddataset" target="_blank">reader buffer</a>)
?Other data reading or processing: you may consider using the <a href="https://www.tensorflow.org/programmers_guide/datasets" target="_blank">tf.data API</a> (if you are not using it now)?
:type.googleapis.com/tensorflow.profiler.BottleneckAnalysisk
unknownTNo step time measured. Therefore we cannot tell where the performance bottleneck is.no*noZno#You may skip the rest of this page.BZ
@type.googleapis.com/tensorflow.profiler.GenericStepTimeBreakdown
  " * 2 : B J R Z b JCPU_ONLYb??No step marker observed and hence the step time is unknown. This may happen if (1) training steps are not instrumented (e.g., if you are not using Keras) or (2) the profiling duration is shorter than the step time. For (1), you need to add step instrumentation; for (2), you may try to profile longer.