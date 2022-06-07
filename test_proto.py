from pyspark import SparkContext
from pyspark.serializers import CloudPickleSerializer
from pyspark.sql.functions import struct
from pyspark.sql.session import SparkSession

from pb.simple_pb2 import SimpleMessage
from pbspark._proto import MessageConverter
from google.protobuf.json_format import MessageToDict

sc = SparkContext(serializer=CloudPickleSerializer())
spark = SparkSession(sc).builder.getOrCreate()
spark.conf.set("spark.sql.session.timeZone", "UTC")
spark.conf.set("spark.sql.execution.arrow.enabled", "true")

example = SimpleMessage(
    name="test",
    quantity=5,
    measure=5.5
)

e = example.SerializeToString()
print(type(e))
p = SimpleMessage()
p.ParseFromString(e)

print(p)

# Everything above

data = [{"value": e}]

df = spark.createDataFrame(data)  # type: ignore[type-var]
df.show()
df.schema

df.printSchema()
mc = MessageConverter()

df_decoded = df.select(mc.from_protobuf(df.value, SimpleMessage).alias("value"))
df_flattened = df_decoded.select("value.*")
df_flattened.show()
