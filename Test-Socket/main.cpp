//#include <QCoreApplication>
//#include <QTcpSocket>
//#include <QJsonDocument>
//#include <QJsonObject>
//#include <QTimer>

////void SendAnimationCommand(const QString& command)
////{
////    QTcpSocket socket;
////    socket.connectToHost("127.0.0.1", 8888);
////    int count = 0;

////    if (socket.waitForConnected())
////    {
////        QByteArray data = command.toUtf8();
////        QTimer* timer = new QTimer(); // 使用 QTimer 对象
////        int delay = 1000; // 设置延迟时间为 1 秒

//////        while (true) {

//////            count++;
//////            timer->setInterval(delay);
//////            socket.write(data);
//////            socket.waitForBytesWritten();
//////            if(count == 10)
//////                break;
//////        }
////        socket.write(data);
////        socket.waitForBytesWritten();
////        socket.disconnectFromHost();
////        while(true) {

////        }
////    }
////    else
////    {
////        qDebug() << "Failed to connect to server.";
////    }
////}


//void SendAnimationCommand(const QJsonObject& commandObject)
//{
//    QTcpSocket socket;
//    socket.connectToHost("127.0.0.1", 8888);

//    if (socket.waitForConnected())
//    {
//        QJsonDocument jsonDoc(commandObject);
//        QByteArray jsonData = jsonDoc.toJson();

//        socket.write(jsonData);
//        socket.waitForBytesWritten();
//        socket.disconnectFromHost();
//    }
//    else
//    {
//        qDebug() << "Failed to connect to server.";
//    }
//}

//int main(int argc, char *argv[])
//{
//    QCoreApplication a(argc, argv);

//    QJsonObject commandObject;
//    commandObject["AnimationName"] = "LeftLeg";
//    commandObject["Speed"] = 5;
//    // 添加其他字段...

//    SendAnimationCommand(commandObject);

//    return a.exec();
//}

#include <QCoreApplication>
#include <QTcpSocket>
#include <QTimer>
#include <QDebug>
#include <QJsonDocument>
#include <QJsonObject>

struct AnimationData
{
    QString AnimationName;
    float Speed;
    bool NeedReturnStateFlag;
};

struct ReturnStateData
{
    QString AnimationName;
    float Speed;
    bool IsCorrect;
};

void ReceiveAnimationCommand(QTcpSocket& socket);

void SendAnimationCommand(const AnimationData& animationData)
{
    QTcpSocket socket;
    socket.connectToHost("127.0.0.1", 8888);

    if (socket.waitForConnected())
    {
        // 序列化数据
        QJsonObject jsonObject;
        jsonObject["AnimationName"] = animationData.AnimationName;
        jsonObject["Speed"] = animationData.Speed;
        jsonObject["NeedReturnStateFlag"] = animationData.NeedReturnStateFlag;

        QJsonDocument jsonDocument(jsonObject);
        QByteArray jsonData = jsonDocument.toJson();

        // 发送 Json 数据
        socket.write(jsonData);
        socket.waitForBytesWritten();

        // 检查状态位，若需要返回状态信息，则阻塞等待信息
        if (animationData.NeedReturnStateFlag)
        {
            ReceiveAnimationCommand(socket);
        }
    }
    else
    {
        qDebug() << "Failed to connect to server.";
    }
}

void ReceiveAnimationCommand(QTcpSocket& socket)
{
    // 等待服务端响应
    socket.waitForReadyRead();

    // 读取响应
    QByteArray responseData = socket.readAll();
    QJsonDocument responseJson = QJsonDocument::fromJson(responseData);
    QJsonObject responseObj = responseJson.object();

    // 反序列化数据
    ReturnStateData returnStateData;
    returnStateData.AnimationName = responseObj["AnimationName"].toString();
    returnStateData.Speed = responseObj["Speed"].toInt();
    returnStateData.IsCorrect = responseObj["IsCorrect"].toBool();

    // debug
    qDebug() << "Received return state message: " << returnStateData.AnimationName;
    qDebug() << "Received return state message: " << returnStateData.Speed;
    qDebug() << "Received return state message: " << returnStateData.IsCorrect;
}

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);

    AnimationData animationData;
    animationData.AnimationName = "LeftLeg";
    animationData.Speed = 5.0;
    animationData.NeedReturnStateFlag = true;

    SendAnimationCommand(animationData);

    return a.exec();
}
