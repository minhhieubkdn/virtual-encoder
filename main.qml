import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15


Window {
    width: 320
    height: 160
    visible: true
    title: qsTr("Virtual Encoder")
    property bool is_connected: false
    property real current_position: 0

    property int enter_index: 0


    function round(number) {
            return Number(number.toFixed(3))
        }

    Connections {
        target: backend

        function onReceivedSerialDataSignal(data)
        {
            tTerminal.text += data
            tTerminal.text += '\n'
            enter_index += 1
            if (enter_index == 4)
            {
                enter_index = 0
                tTerminal.text = data + '\n'
            }
        }

        function onGetOpeningPorts(port_list)
        {
            cbbPorts.model = port_list
        }

        function onConnectedPort(is_cn)
        {
            is_connected = is_cn
            if (is_cn)
            {
                btConnect.text = "Disconnect"
            }
            else
            {
                btConnect.text = "Connect"
            }
        }

        function onSetCurrentPosition(current_pos)
        {
            current_position = round(current_pos)
            tePos.text = round(current_pos)
        }
    }

    Column {
        id: column
        anchors.fill: parent

        Row {
            id: row1
            height: 30
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top

            Text {
                id: lbspeed
                width: 160
                height: 30
                text: qsTr("Speed")
                font.pixelSize: 12
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            TextEdit {
                id: teSpeed
                height: 30
                text: qsTr("0")
                anchors.left: lbspeed.right
                anchors.right: parent.right
                font.pixelSize: 12
                horizontalAlignment: Text.AlignLeft
                verticalAlignment: Text.AlignVCenter
                leftPadding: 8
                anchors.leftMargin: 0
                anchors.rightMargin: 0

                onEditingFinished: {
                    if (is_connected)
                        backend.set_speed(parseFloat(teSpeed.text))
                }
                Keys.onReturnPressed: {
                    if (is_connected)
                        backend.set_speed(parseFloat(teSpeed.text))
                }
            }
        }

        Row {
            id: row2
            height: 30
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: row1.bottom
            anchors.topMargin: 0
            Text {
                id: lbspeed1
                width: 160
                height: 30
                text: qsTr("Position")
                font.pixelSize: 12
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }

            TextEdit {
                id: tePos
                height: 30
                text: qsTr("0.0")
                anchors.left: lbspeed1.right
                anchors.right: parent.right
                font.pixelSize: 12
                horizontalAlignment: Text.AlignLeft
                verticalAlignment: Text.AlignVCenter
                leftPadding: 8
                anchors.rightMargin: 0
                anchors.leftMargin: 0
            }
        }

        Row {
            id: row3
            height: 30
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: row2.bottom
            anchors.topMargin: 0

            ComboBox {
                id: cbbPorts
                width: 160
                height: 30
                anchors.left: parent.left
                anchors.top: parent.top
                anchors.topMargin: 0
                anchors.leftMargin: 0
            }

            Button {
                id: btConnect
                width: 100
                height: 30
                text: qsTr("Connect")
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.rightMargin: 50
                anchors.topMargin: 0
                onClicked: {
                    if (!is_connected)
                    {
                        backend.connect_port(cbbPorts.currentText)
                    }else{
                        backend.close_serial(true)
                    }
                }
            }
        }

        Row {
            id: row4
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: row3.bottom
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 0
            anchors.topMargin: 0

            Text {
                id: tTerminal
                anchors.fill: parent
                font.pixelSize: 12
                rightPadding: 8
                bottomPadding: 8
                topPadding: 8
                leftPadding: 8
            }
        }
    }
}
