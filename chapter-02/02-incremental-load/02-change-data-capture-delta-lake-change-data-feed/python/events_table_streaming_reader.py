from threading import Thread, Event

from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession

if __name__ == "__main__":
    spark_session = (configure_spark_with_delta_pip(SparkSession.builder.master("local[*]")
                                                    .config(
        "spark.databricks.delta.properties.defaults.enableChangeDataFeed", "true")
                                                    .config("spark.sql.extensions",
                                                            "io.delta.sql.DeltaSparkSessionExtension")
                                                    .config("spark.sql.catalog.spark_catalog",
                                                            "org.apache.spark.sql.delta.catalog.DeltaCatalog")
                                                    ).getOrCreate())

    events_table_created = Event()


    def load_data_to_the_events_table(table_created: Event):
        partitions = ['date=2023-11-01', 'date=2023-11-02', 'date=2023-11-03',
                      'date=2023-11-04', 'date=2023-11-05', 'date=2023-11-06', 'date=2023-11-07']
        base_dir = '/tmp/dedp/ch02/incremental-load/change-data-capture/input/'
        for partition in partitions:
            print(f'Loading partition {partition}')
            path_to_load = f'{base_dir}/{partition}'
            input_dataset = (
                spark_session.read.schema('visit_id STRING, event_time TIMESTAMP, user_id STRING, page STRING')
                .format('json').load(path_to_load))
            if not table_created.is_set():
                (input_dataset.write.format('delta').mode('overwrite').saveAsTable('events'))
                print('Events table created')
                table_created.set()
            else:
                (input_dataset.write.format('delta').insertInto('events'))


    thread = Thread(target=load_data_to_the_events_table, kwargs={'table_created': events_table_created})
    thread.start()

    while not events_table_created.wait(timeout=1):
        if not thread.is_alive():
            raise RuntimeError('The loader thread failed before creating the events table')

    events = (spark_session.readStream.format('delta')
              .option('maxFilesPerTrigger', 4)
              .option('readChangeFeed', 'true')
              .option('startingVersion', 0).table('events'))

    query = events.writeStream.format('console').start()

    query.awaitTermination()
