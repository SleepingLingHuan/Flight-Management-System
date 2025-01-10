# Flight-Management-System
/**
 * @copyright
 * Project: Data Structure Course Design Project 1, Flight-Management-System
 * Course: Data Structure (2024)
 * Institution: School of Computer Science, China University of Geosciences (Wuhan)
 * Major: Software Engineering
 * Author: Ge Xuanyu
 * Date: January 10, 2025
 * 
 * All rights reserved. This project is for educational purposes only and may not be used, distributed, or modified without explicit permission from the author and the institution.

 * @版权声明
 * 项目名称：数据结构课程设计项目1，飞机票航班管理系统
 * 课程名称：数据结构（2024年）
 * 所属学院：中国地质大学（武汉）计算机学院
 * 专业：软件工程
 * 作者：葛轩宇
 * 日期：2025年1月10日
 * 
 * 版权所有。本项目仅限于教育用途，未经作者及所属学院明确许可，不得用于其他用途、分发或修改。

 */

程序使用的数据由dataSet.py随机生成，请先运行dataSet.py。也可直接使用已有的FlightDataset.txt  
航班管理系统程序为main.py  
1.航班信息管理：可新增或删除航班。新增航班需要输入全部航班信息，删除航班仅需输入航班ID。  
2.航班动态管理：可设置航班延误时间或取消航班。航班被取消后会自动检查该航班是否已被用户购票，若是则自动退票。  
3.票务管理：用户可直接购票、退票和预约抢票。购票时需要输入用户个人ID、航班ID和购票数量，若航班可购票且机票充足则购票成功，会有购票确认提示。退票时会验证用户在对应航班的购票情况，不可在未购票的情况下退票或超额退票。预约抢票使用优先队列，优先级高的先抢票，抢票时验证航班是否可购票且机票充足，若是则购票，反之提示抢票失败。  
4.用户界面：左侧会显示所有已购票的用户ID，点击对应用户ID后可在右侧查看该用户的购票情况。  
5.票务查询：输入出发城市和目的城市，选择排序依据，可查看全部符合要求的航班详细信息。也可勾选仅查看可购票航班，此时不会显示机票余额为零或被取消的航班。  
6.航班查询：根据输入的航班ID查询对应航班的详细信息。  
7.代替航班推荐：当两个城市无可用的直达航班时，可查询两个城市之间的替代航班，即多次转机后抵达目的城市。代替航班会输出全部可行方案，每个方案会输出其中的航班信息。  

 The data used by the program is randomly generated by dataSet.py. Please run dataSet.py first. Alternatively, you can directly use the existing FlightDataset.txt.
The flight management system program is main.py.

1. Flight Information Management:
   - You can add or delete flights.
   - When adding a flight, all flight information must be provided.
   - When deleting a flight, only the flight ID is required.

2. Flight Status Management:
   - You can set flight delays or cancel flights.
   - When a flight is canceled, the program will automatically check if tickets for the flight have already been purchased by users. If so, refunds will be processed automatically.

3. Ticket Management:
   - Users can purchase tickets, request refunds, and reserve tickets for high-demand flights.
   - Purchasing tickets: Users need to provide their personal ID, the flight ID, and the number of tickets to purchase. If the flight is available for ticket purchase and there are enough tickets, the purchase will succeed, and a confirmation message will be displayed.
   - Requesting refunds: The system will verify the user's ticket purchase record for the corresponding flight. Refunds cannot be processed for flights without tickets purchased, nor can users request refunds for more tickets than they have purchased.
   - Reserving tickets: Reservations are handled using a priority queue, where users with higher priority will get tickets first. During the process, the system will verify if the flight is available for ticket purchase and if there are enough tickets. If conditions are met, the reservation succeeds; otherwise, a failure message is displayed.

4. User Interface:
   - On the left side, the interface displays the IDs of all users who have purchased tickets.
   - Clicking on a user ID displays the ticket purchase details for that user on the right side.

5. Ticket Query:
   - By inputting the departure city and destination city and selecting sorting criteria, users can view detailed information on all flights that meet the specified conditions.
   - Users can also check the option to view only flights that have tickets available for purchase. In this case, flights with zero remaining tickets or canceled flights will not be displayed.

6. Flight Query:
   - Users can query detailed information about a specific flight by entering its flight ID.

7. Alternative Flight Recommendations:
   - When there are no direct flights available between two cities, users can search for alternative flights.
   - The system will provide all feasible multi-stop flight plans to reach the destination city.
   - Each plan will include detailed information about the flights involved.
