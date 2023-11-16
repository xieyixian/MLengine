import os
import pika
import json
import pandas as pd
from datetime import datetime
from ml_engine import MLPredictor
from matplotlib import pyplot as plt

received_data = []

def callback(ch, method, properties, body):
    try:
        # 解析收到的JSON消息
        # data = json.loads(body.decode('utf-8'))
        data = json.loads(body.decode('utf-8'))
        # data_new = pd.DataFrame()
        # for i in range(len(data)):
        #     data_new.loc[i, 'Timestamp'] = data[i].get('Timestamp', '')
        #     data_new.loc[i, 'Value'] = data[i].get('Value', '')
        #
        # print(data_new)
        #
        # # Append data to the list
        # received_data.extend(data)
        #
        # # 处理并绘图
        process_and_plot(data)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

def process_and_plot(data):
    # 转换数据为DataFrame
    # data_new = pd.DataFrame()
    # for i in range(len(data)):
    #     data_new.loc[i, 'Timestamp'] = data[i].Timestamp
    #     data_new.loc[i, 'Value'] = data[i].get('Value', '')

    # print(data_new)
    # print(data[1])
    # Convert the list of dictionaries to DataFrame
    data_df = pd.DataFrame.from_dict(data, orient='index')
    data_df['Timestamp'] = pd.to_datetime(data_df['Timestamp'], format='%Y-%m-%d %H:%M:%S')
    data_df = data_df.sort_values(by='Timestamp').reset_index(drop=True)
    data_df['Timestamp'] = data_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    print(data_df)


    if not data_df.empty:

        # Define the current timestamp
        current_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        save_fpath = os.path.join(os.getcwd(), "images", f"{current_timestamp}_figure.png")

        plt.figure(figsize=(8, 4), dpi=200)
        # Plot data into canvas
        plt.plot(data_df["Timestamp"], data_df["Value"], color="#FF3B1D", marker='.', linestyle="-")
        plt.title("Example data for demonstration")
        plt.xlabel("DateTime")
        plt.ylabel("Value")

        # Save as file
        plt.savefig(save_fpath)
        # Directly display
        # plt.show()


        # Create ML engine predictor object
        predictor = MLPredictor(data_df)
        # Train ML model
        predictor.train()
        # Do prediction
        forecast = predictor.predict()
        # Get canvas
        fig = predictor.plot_result(forecast)
        save_path = os.path.join(os.getcwd(), "images", f"{current_timestamp}_prediction.png")
        fig.savefig(save_path)
        fig.show()

def receive_data_from_rabbitmq():
    rabbitmq_host = "192.168.0.100"
    rabbitmq_port = 5673
    rabbitmq_user = "xyh123"
    rabbitmq_password = "123456"
    rabbitmq_queue = "CSC8112"

    # 建立到RabbitMQ的连接
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    parameters = pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()

    # 声明队列
    channel.queue_declare(queue=rabbitmq_queue)

    # 设置回调函数，处理接收到的消息
    channel.basic_consume(queue=rabbitmq_queue, on_message_callback=callback, auto_ack=True)

    print("Waiting for messages. To exit press CTRL+C")
    # 开始监听消息
    channel.start_consuming()

if __name__ == '__main__':
    receive_data_from_rabbitmq()
