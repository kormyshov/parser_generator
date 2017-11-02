from levenstein_metric import LevensteinMetric
from avg_aggregator import AvgAggregator
from primitive_algorithm import PrimitiveAlgorithm
from quality_control import QualityControl

metric = LevensteinMetric()
aggregator = AvgAggregator()

algorithm = PrimitiveAlgorithm()
control = QualityControl(metric, aggregator)
print("Quality =", control.get_quality(algorithm))