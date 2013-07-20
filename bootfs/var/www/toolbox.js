
recheckAccount();

// ********************** Reboot Function Start ********************** //
function Reboot(){
 var sure = confirm(decode(showText(148)));
 if(sure)
  document.location="system_reboot.htm";
}

function Reset_2_Def(){
 var sure = confirm(decode(showText(147)));
 if(sure){
  getContent('','/cgi-bin/toolbox.cgi?Reset_2_Def','',false);
  document.location="system_reboot.htm";
 }
}
// ********************** Reboot Function End ************************* //

// ********************** Firmware Upgrade Function Start ************************ //
function DisableButton(){
 document.getElementById('DownloadFirmware').disabled=true;
}

function CheckNEW(){
 //showBackgroundImage('ShowUpLoadFile')
 showBackgroundImage('wait_message');
 getContent('','/cgi-bin/toolbox.cgi?CheckNEW',"function:showNewFirmware");
}

function showNewFirmware(msg){
 msg = msg.split("\n");
 hiddenBackgroundImage('wait_message');
 if(msg[0].indexOf('NoConnect')!=-1){
  document.getElementById('DownloadFirmware').disabled=true;
  window.document.getElementById('CheckVer').innerHTML = msg[1];
 } else if(msg[0]==""){
  document.getElementById('DownloadFirmware').disabled=true;
  window.document.getElementById('CheckVer').innerHTML = 'No new version.';
 } else {
  document.getElementById('DownloadFirmware').disabled=false;
  window.document.getElementById('CheckVer').innerHTML = 'SitecomNas v'+msg[0];
  var xmlDoc = parseXML(getContent('',"version.xml?","html",false));
  var xmlDownloadURL = getURL(xmlDoc,"url");
  window.document.getElementById('URL').innerHTML = '<INPUT id=DownLoadURL value=\"'+xmlDownloadURL+'\" type=hidden>';
 }
}

function DownloadFirmware(){
 alert(decode(showText(239)));
 showBackgroundImage('ShowUpLoadFile');
 var DownLoadURL = document.getElementById('DownLoadURL').value;
 getContent('','/cgi-bin/toolbox.cgi?DownloadFirmware&'+DownLoadURL,"function:showConfirmUpgrade");
}

function showConfirmUpgrade(msg){
 hiddenBackgroundImage('ShowUpLoadFile');
 var DownLoadURL = document.getElementById('DownLoadURL').value;
 FileName = DownLoadURL.split("\/");

 for (i=0; i<FileName.length ; i++){
  var str = '/tmp/'+FileName[i];
  if(str.indexOf('.bin')!=-1){
   ppp = str;
   break;
  }
 }

 if(msg.indexOf('NOT')!=-1)
  window.document.getElementById('CheckVer').innerHTML =  "Server returned error: HTTP/1.0 404 File download error, Please try again.";
 else
  document.location="firmware_upgrade.htm?path="+ppp;
}

function UpLoadFile(){
 var filename = document.getElementById("UploadFile").value;
 if (filename==""){
  alert(decode(showText(149)));
  return false;
 } else {
  showBackgroundImage('ShowUpLoadFile')
 }
}

function UpLoadCancel(){
 window.document.getElementById('Upload').innerHTML = '<input type=\"file\" size=\"25\" maxlength=\"31\" name=\"file\" id=\"UploadFile\" />';
}

function Decompression(){
 showBackgroundImage('Kernel_upgrade');
 getContent('','/cgi-bin/toolbox.cgi?Kernel_upgrade&'+ppp,"function:Kernel_upgrade");
}

function Kernel_upgrade(msg){
 hiddenBackgroundImage('Kernel_upgrade');
 if(msg.indexOf('finish')!=-1){
  window.document.getElementById("Kernel_upgrade").innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;OK";
  finish=1;
 } else if(msg.indexOf('error')!=-1){
  window.document.getElementById("Kernel_upgrade").innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;<font color=darkred>MD5 check error !!!</font>";
 } else {
  window.document.getElementById("Kernel_upgrade").innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;don't need upgrade";
 }
 showBackgroundImage('Bootfs_upgrade');
 getContent('','/cgi-bin/toolbox.cgi?Bootfs_upgrade&'+ppp,"function:Bootfs_upgrade");
}

function Bootfs_upgrade(msg){
 hiddenBackgroundImage('Bootfs_upgrade');
 if(msg.indexOf('finish')!=-1){
  window.document.getElementById("Bootfs_upgrade").innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;OK";
  finish=1;
 } else if(msg.indexOf('error')!=-1){
  window.document.getElementById("Bootfs_upgrade").innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;<font color=darkred>MD5 check error !!!</font>";
 } else {
  window.document.getElementById("Bootfs_upgrade").innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;don't need upgrade";
 }
 showBackgroundImage('FileSystem_upgrade');
 getContent('','/cgi-bin/toolbox.cgi?FileSystem_upgrade&'+ppp,"function:FileSystem_upgrade");
}

function FileSystem_upgrade(msg){
 hiddenBackgroundImage('FileSystem_upgrade');
 if(msg.indexOf('finish')!=-1){
  window.document.getElementById("FileSystem_upgrade").innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;OK";
  finish=1;
 } else if(msg.indexOf('error')!=-1){
  window.document.getElementById("FileSystem_upgrade").innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;<font color=darkred>MD5 check error !!!</font>";
 } else {
  window.document.getElementById("FileSystem_upgrade").innerHTML = "&nbsp;&nbsp;&nbsp;&nbsp;don't need upgrade";
 }
 if (finish==1)
  UpgradeFinish();
}

function UpgradeFinish(){
 var sure = confirm(decode(showText(150)));
 if(sure)
  document.location="system_reboot.htm";
}

function getParameter(parameterName) {
	var strQuery = location.search.substring(1);
	var paramName = parameterName + "=";
	if (strQuery.length > 0) {
		begin = strQuery.indexOf(paramName);
		if (begin != -1) {
			begin += paramName.length;
		end = strQuery.indexOf("&" , begin);
		if ( end == -1 ) end = strQuery.length
			return unescape(strQuery.substring(begin, end));
		}
		return "null";
	}
}

// ********************** Firmware Upgrade Function End ************************** //

// ********************** parseXML Function Start ************************** //

function parseXML(xmlText){
 var xmlDoc;
 try{
  xmlDoc=new ActiveXObject("Microsoft.XMLDOM");
  xmlDoc.async="false";
  xmlDoc.loadXML(xmlText);
 }

 catch(e){
  try{
   parser=new DOMParser();
   xmlDoc=parser.parseFromString(xmlText,"text/xml");
  }
  catch(e){
   alert(e.message);
   return;
  }
 }
 return xmlDoc;
}

function getURL(xmlDoc,key){
 var _key = xmlDoc.getElementsByTagName(key)[0].firstChild.nodeValue;
 if (_key)
  return _key.Trim();
}

String.prototype.Trim = function() {
 return this.replace(/(^\s*)|(\s*$)/g,"");
}

// ********************** parseXML Function End ************************** //

// ********************** Install package Start ************************** //
function go(path){
 var str="";
 var ppp_length=path.length;
 var now_path = path.substr(5,4096);
 if(ppp_length<=8)
 str='/';
 window.document.getElementById('now_path').innerHTML = '<b>'+showText(191)+'&nbsp;'+str+now_path+'</b>';
 getContent('DirList','/cgi-bin/firmwareDir.cgi?'+path);
 parent.calcHeight('parent');
 hiddenBackgroundImage('wait_message');
}

function install_pkg(path){
  showBackgroundImage('install_message')
  getContent('','/cgi-bin/toolbox.cgi?install_pkg&'+path,"function:pkg_finish");
}

function pkg_finish(msg){
 if(msg.indexOf('ok')!=-1)
  alert(decode(showText(247)));
 else if(msg.indexOf('exist')!=-1)
  alert(decode(showText(248)));
 else if(msg.indexOf('no_device')!=-1)
  alert(decode(showText(250)));
 else if(msg.indexOf('no_remnant_size')!=-1)
  alert(decode(showText(251)));
 else
  alert(decode(showText(249)));
   
showBackgroundImage('wait_message')
location.replace ('install_pkg.htm');
}

function install_pkg_status(){
 showBackgroundImage('wait_message');
 getContent('','/cgi-bin/services.cgi?Package_folder',"function:packageFolderControl");
 }

function packageFolderControl(msg){
 var data = new Array("DelPackage","StartPackage","StopPackage","package_all");
 if(msg.indexOf('NoDisk')!=-1){
  for (i=0; i<data.length && data[i] != "" ; i++){
  document.getElementById(data[i]).disabled='false';
  }
 }
 getContent('','/cgi-bin/services.cgi?Install_pkg_list',"function:ShowInstallPkgList");
}

function ShowInstallPkgList(msg){
 msg = msg.split("\n");
 var name = '';
 var oTable=window.document.getElementById('PackageListData');
 var rowNum=oTable.rows.length;
 if(rowNum>3){
  rowNum = rowNum - 1;
  for(rIndex=2;rIndex<rowNum;rIndex++)
   oTable.deleteRow(-1);
 }
 
 var isIE = navigator.userAgent.search("MSIE") > -1; 
 var thisHREF = document.location.href;
 thisHREF = thisHREF.split( "/" );
 var IP = thisHREF[2];

 for (i=0; i<msg.length && msg[i] != "" ; i++){
  var table_height=28;
  var oTr=oTable.insertRow(-1);
  data = msg[i].split("^");
  for (j=0; j<data.length && data[j] != "" ; j++){
   oCell=oTr.insertCell(j);
   oCell.style.cssText="text-align: center;color: #000000;";

   if(j==0){
    name = data[1].split("%");
    data[j]='<input type=checkbox id=package_'+i+' value=\"'+name[0]+'\"';
	if(name[1]=="Twonkymedia")
		data[j] += " Disabled=\"true\" />";
	else
		data[j] += " />";
   }

   if(j==1){
    name = data[j].split("%");
    oCell.style.cssText="text-align: center;color: #000000;padding: 0px 0px 0px 10px;";
    data[j]=name[1];
   }
   if(j==3){
    if((data[4]=="ON")&&(data[3]=="0")){
     if((data[1]=="PrinterServer" || data[1]=="TimeMachine")&&(isIE)){
     oCell.style.cssText="text-align: center;color: #008800;padding: 0px 0px 0px 10px;";
     data[j]='<a href=\"file://'+IP+'\" target=\"_blank\">'+IP;
     }else{
      data[j]='<a href=\'javascript:alert(decode(showText(252)));\' >'+IP;
     }
    }else if((data[4]=="ON")&&(data[3]!="0")){
	 if(data[1]=="SqueezeCenter"){
      oCell.style.cssText="text-align: center;color: #008800;padding: 0px 0px 0px 10px;";
      data[j]='<a href=\"http://'+IP+':'+data[j]+'\" target=\"_blank\" onClick=alert(decode(showText(254))); >'+IP+':'+data[j];
     }else{ 	 
      oCell.style.cssText="text-align: center;color: #008800;padding: 0px 0px 0px 10px;";
      data[j]='<a href=\"http://'+IP+':'+data[j]+'\" target=\"_blank\">'+IP+':'+data[j];
     }
    }else{
     data[j]='';
    }
   }
   
   str = data[j];
   //oCell.style.backgroundColor="#FFFFFF";
   oCell.innerHTML=str;
  }
 }
 //document.getElementById('DelPackage').disabled='false';
 window.document.getElementById('Value').innerHTML = '<INPUT id=Now_Value value=\"'+i+'\" type=hidden>';
 parent.calcHeight('parent');
 hiddenBackgroundImage('wait_message');
} 

function SelectAll(){
 var num = document.getElementById('Now_Value').value;
 var checked=document.getElementById("package_all").checked;
 for (x=0; x<num; x++){
  pkg_num = document.getElementById("package_"+x).value;
  if(pkg_num!="4")
    document.getElementById("package_"+x).checked=checked;
 }
}

function PackageAction(id){
 var num = document.getElementById('Now_Value').value;
 var str = '';
 for (x=0; x<num; x++){
  if (document.getElementById("package_"+x).checked==true)
   var VALUE = document.getElementById("package_"+x).value+'^';
  else
   continue;

   str += VALUE;
 }
 if(str==''){
  return false;
 } else {
  if(id=="del"){
   showBackgroundImage('del_message');
   if (confirm(decode(showText(253))))
    getContent('','/cgi-bin/services.cgi?PackageAction&'+id+'&'+str,'function:showPackageMsg');
   else
    location.replace ('install_pkg.htm');
  } else if(id=="start"){
   showBackgroundImage('start_message');
   getContent('','/cgi-bin/services.cgi?PackageAction&'+id+'&'+str,'function:showPackageMsg');
  } else {
   showBackgroundImage('stop_message');
   getContent('','/cgi-bin/services.cgi?PackageAction&'+id+'&'+str,'function:showPackageMsg');
  }
 }
}

function showPackageMsg(){
 showBackgroundImage('wait_message');
 location.replace ('install_pkg.htm');
}
  
// ********************** Install package End ************************** //
