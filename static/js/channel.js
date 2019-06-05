document.addEventListener('DOMContentLoaded',()=>{

    // Connect to websocket
    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

    // 获取当前 channel 名（就想到这种不是很优美的方案）
    // TODO: 隐含着频道名不能含有 /
    var channel_name = window.location.pathname.split('/')[2];

    console.log(location.protocol + '//' + document.domain + ':' + location.port);

    // When connected, configure buttons
    socket.on('connect', () => {

        // Each button should emit a "submit vote" event
        document.querySelector('#send_msg').onclick = () =>{

            const content = document.querySelector('#msg_content').value;
            console.log("发送的：" + content);
            socket.emit('msg', {
                'channel_name':channel_name,
                'content':encodeURI(content)
            });

            document.querySelector('#channel-number').innerHTML =
                +document.querySelector('#channel-number').innerHTML + 1;
        };
    });

    // 收到消息
    // 消息格式
    // {
    //     'channel_name':xxx,
    //     'user':xxx,
    //     'content':xxx
    //
    // }
    socket.on('broad_msg', msg => {
        if (msg['channel_name'] != channel_name)
            return;
        const user = msg['user'];
        const content = msg['content'];
        const time = msg['time'];
        const a = document.createElement('a');
        a.className = "list-group-item list-group-item-action flex-column";
        a.innerHTML = '<div class="d-flex w-100 justify-content-between">'        +
                        `<h5 class="mb-1 text-success">${user} <small>(${time})</small> :</h5></div>`      +
                        `<p class="mb-1">${decodeURI(content)}</p>`;
        document.querySelector('#msgs').append(a)
        console.log(content)
    });
});