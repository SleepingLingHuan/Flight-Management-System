import random
import datetime

#城市列表
cities = [
    "Beijing", "Shanghai", "Guangzhou", "Shenzhen", "Chengdu", "Chongqing", "Hangzhou",
    "Nanjing", "Wuhan", "Changsha", "Kunming", "Xi'an", "Lanzhou", "Yinchuan", "Hohhot",
    "Dalian", "Harbin", "Changchun", "Shenyang", "Tianjin"
]

#航班数据生成函数
def generate_dataset(num_flights=300):
    flights = []
    start_time = datetime.datetime(2024, 1, 1, 6, 0)
    for i in range(1, num_flights + 1):
        flightID = f"G{1000 + i}"
        departureCity = random.choice(cities)
        destinationCity = random.choice([city for city in cities if city != departureCity])
        stopover = "None"
        departureDate = (datetime.date(2024, 1, 1) + datetime.timedelta(days=(i // 10))).strftime("%Y%m%d")

        #departureTime按升序排列
        departureTime = start_time.strftime("%H:%M")
        duration = random.randint(45, 180)
        arrivalTime = (start_time + datetime.timedelta(minutes=duration)).strftime("%H:%M")

        #更新下一次的出发时间
        start_time += datetime.timedelta(minutes=random.randint(30, 120))

        price = random.randint(200, 1000)
        tickets = random.randint(50, 200)
        isDelay = random.choice([0, 1])
        delayTime = random.randint(0, 120) if isDelay else 0
        isCancelled = 0
        isForSale = 1

        flights.append(f"{flightID} {departureCity} {destinationCity} {stopover} {departureDate} {departureTime} {arrivalTime} {price} {tickets} {isDelay} {delayTime} {isCancelled} {isForSale}")

    return flights

#生成航班数据并写入文件
dataset = generate_dataset(300)
output_file_path = r"E:\数据结构课程设计\Problem1\flightDataSet.txt"

with open(output_file_path, 'w') as file:
    file.write("\n".join(dataset))