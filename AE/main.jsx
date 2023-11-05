var origTimeDisplayType = app.project.timeDisplayType;
var origFramesCountType = app.project.framesCountType;
function setTimeDisplayTypeTo(type){
    switch(type){
        case 'timecode':
            app.project.timeDisplayType=2012;
            break;
        case 'frame':
            app.project.timeDisplayType=2013;
            break;
        case 'orig':
            app.project.timeDisplayType=origTimeDisplayType;
            break;
    }
}
function setFramesCountTypeTo(type){
    switch(type){
        case 'from1':
            app.project.framesCountType=FramesCountType.FC_START_1;
            break;
        case 'from0':
            app.project.framesCountType=FramesCountType.FC_START_0;
            break;
        case 'orig':
            app.project.framesCountType=origFramesCountType;
            break;
    }
}
function checkCurComp () {
    var curComp = app.project.activeItem;
    if (!curComp || !(curComp instanceof CompItem)) {
        alert('select current comp first');
        return;
    }
    var origFps = curComp.frameRate;
    var dropFrame = curComp.dropFrame;
    switch (origFps.toFixed(2)){
        case '29.97':
            if (!dropFrame) var fps = 30;
            break;
        case '59.94':
            if (!dropFrame) var fps = 60;
            break;
        default:
            var fps = origFps;
    }
    var layers = curComp.layers;
    setTimeDisplayTypeTo('frame');
    for (var i = 1, l = layers.length; i <= l; i++) {
        var layerName = layers[i].name;
        var frameIn = timeToCurrentFormat(layers[i].inPoint,origFps)-0;
        var frameOut = timeToCurrentFormat(layers[i].outPoint,origFps)-1;
        alert(frameIn);
        alert(frameOut);
    }
    setTimeDisplayTypeTo('timecode');
    for (var i = 1, l = layers.length; i <= l; i++) {
        var timeIn = timeToCurrentFormat(layers[i].inPoint,origFps);
        var timeOut = timeToCurrentFormat(layers[i].outPoint,origFps);
        alert(timeIn);
        alert(timeOut);
    }
    setFramesCountTypeTo('orig');
    setTimeDisplayTypeTo('orig');
}
var layer1 = app.project.activeItem.layers[1];
var fps = app.project.activeItem.frameRate;
var timeIn = timeToCurrentFormat(layer1.inPoint,fps);
alert(layer1.property("Text").value)
alert(fps);
alert(timeIn);

// checkCurComp();
