
/**
 * 当页面加载完毕的时候，注册相关组件
 */
window.addEventListener('load',registeTools,false);
//---------------------------局部方法和变量
/*
 * 点击更多工具，下面工具栏的出现和消失
 */
function moreTools(){
	var moretools=document.getElementById("moretools");
	var bottom=document.getElementById("bottom");
	if(moretools.style.display=="none"){
		moretools.style.display="block";
		bottom.style.height="50%";
	}else{
		moretools.style.display="none";
		bottom.style.height="auto";
	}
}
/**
 * 正在输入，需要出现提交按钮，消失moretools
 */
function inputingMeg(){
	//首先应该将页面端中工具面板进行隐藏，避免缩放
	document.getElementById("moretools").style.display="none";
	var moreIcon=document.getElementById("moreicon");
	if(!(moreIcon.style.display=="none")){
		moreIcon.style.display="none";
	  var btnSend=document.getElementById("btnsend");
	  btnSend.style.display="block";
	}
}


// 建立websocket链接

var websocket = new WebSocket('ws://127.0.0.1:8000/chat/')

// 获取后端返回到数据
websocket.onmessage = function (e) {
	if(e.data.split(':')[0] == '系统提示') {
		var msg_info = '<p style="text-align: center">' + e.data + '</p>'
		$('#chatpanel').append(msg_info)
	}
	// 接收数据调用方法
	receiveMessage(e.data)
}

/*
 * 聊天发送信息
 *
 */
function sendMsg(){
	var inputNode=document.getElementById("inputtext");
	var text=inputNode.value;
	if(!text==""){
		//发布消息
		//需要做一些 和服务器交互的ajax事情
		var msg=new Message('katey2658','我:' + text,'/static/img/photo.jpg');
    addMsgNode(msg);
    getStart();
    inputNode.value="";

    // 发送信息
	websocket.send(text)
	}
}

//收到消息后的反应
function receiveMessage(message){
	//将消息添加到节点上
	var msg=new Message('other',message,'/static/img/photo2.jpg');
	addMsgNode(msg);
}


/**
 * 关于从新开始，让状态规整个i他
 * @return {[type]} [description]
 */
function getStart(){
	var inputNode=document.getElementById("inputtext");
	if(inputNode.value==""){
		var btnSend=document.getElementById("btnsend");
	    btnSend.style.display="none";
	    var moreIcon=document.getElementById("moreicon");
	    moreIcon.style.display="block";
	}
}

/**
 * 添加消息节点
 */
function addMsgNode(msg){
	var msgNode=document.createElement("div");
	var photoNode=document.createElement("div");
	var photoImg=document.createElement("img");
	var textNode=document.createElement("div");
	var textSpan=document.createElement("span");
	textSpan.innerText=msg.text;
	textNode.appendChild(textSpan);
	photoImg.src=msg.photo;
	photoNode.appendChild(photoImg);
	if(msg.userName=='katey2658'){
		//是自己 ，先加文字，剧右边
		msgNode.appendChild(photoNode);
		msgNode.appendChild(textNode);
		msgNode.className="msg-right";
	}else{
		//不是自己,先加图片,再加文字
		msgNode.appendChild(photoNode);
		msgNode.appendChild(textNode);
		msgNode.className="msg-left";
	}
	photoNode.className="photo";
	textNode.className="text";
	//最后添加到面板上
	var chatPanel=document.getElementById("chatpanel");
	chatPanel.appendChild(msgNode);
}

/**
 * 一个信息类
 * @param {Object} username
 * @param {Object} text
 * @param {Object} photo
 */
function Message(username,text,photo){
	this.userName=username;
	this.text=text;
	this.time=new Date();
	this.photo=photo;
}

/**
 * 注册相关组件工具
 * @return {[type]} [description]
 */
function registeTools() {
	var albumTool=document.getElementById('album');
	var useCameraTool=document.getElementById('useCamera');
	var videoCallTool=document.getElementById('videoCall');
	var locationTool=document.getElementById('location');
	var redPocketTool=document.getElementById('redPocket');
	var transferTool=document.getElementById('transfer');
	var contactCardTool=document.getElementById('contactCard');
	var favoritesTool=document.getElementById('favorites');
  //主要工具按钮的设置
	albumTool.onclick=album;
	useCameraTool.onclick=useCamera;
	videoCallTool.onclick=videoCall;
	// locationTool.onclick=myLocation;
	redPocketTool.onclick=redPocket;
	redPocketTool.onclick=transfer;
	contactCardTool.onclick=contactCard;
	favoritesTool.onclick=favorites;
}

function returnToHome() {
	history.go(-1);
}


