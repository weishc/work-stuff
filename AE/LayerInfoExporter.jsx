var origTimeDisplayType = app.project.timeDisplayType;


function writingFilesEnabled() {
    var version12Check = (
        parseFloat( app.version ) > 12.0 ||
        ( parseFloat( app.version ) === 12.0 &&
            app.buildNumber >= 264 ) ||
        app.version.substring( 0, 5 ) !== "12.0x" );
    var mainSectionStr = ( version12Check ) ? "Main Pref Section v2" : "Main Pref Section";
    var version16Check = ( parseFloat( app.version ) > 16.0 );
    var securitySetting = app.preferences.getPrefAsLong( 
        mainSectionStr, "Pref_SCRIPTING_FILE_NETWORK_SECURITY" 
        );
    if ( securitySetting === 0 ) {
        alert( 'To run this script correctly, you must enable the  \
"Allow scripts to write files and..." option then re-run this script.  \
You can find it in Edit->Preferences->Scripting & Experssion.' );
        ( version16Check ) ? app.executeCommand( 3131 ): app.executeCommand( 2359 );
    }
    return ( securitySetting === 1 );
}

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

function framesToTC(frames, fps, dropFrame, CHT) {
    // Duncan/Heidelberger method.
    var spacer = ':';
    if (dropFrame){
        var spacer2 = ';';
    
        var dropFrames = Math.round(fps * 0.066666);
        var framesPerHour = Math.round(fps * 3600);
        var framesPer24Hours = framesPerHour * 24;
        var framesPer10Minutes = Math.round(fps * 600);
        var framesPerMinute = Math.round(fps) * 60 - dropFrames;
        frames = frames % framesPer24Hours;
        var d = Math.floor(frames / framesPer10Minutes);
        var m = frames % framesPer10Minutes;
        if (m > dropFrames) {
            frames = frames + (dropFrames * 9 * d) + dropFrames * Math.floor((m - dropFrames) / framesPerMinute);
        } else {
            frames = frames + dropFrames * 9 * d;
        }
        var frRound = Math.round(fps);
        var hr = Math.floor(frames / frRound / 60 / 60);
        var mn = Math.floor((frames / frRound / 60) % 60);
        var sc = Math.floor((frames / frRound) % 60);
        var fr = Math.floor(frames % frRound);
    } else {
        fps = Math.round(fps);
        var spacer2 = spacer;
        var frHour = fps * 3600;
        var frMin = fps * 60;
        hr = Math.floor(frames / frHour);
        mn = Math.floor((frames - hr * frHour) / frMin);
        sc = Math.floor((frames - hr * frHour - mn * frMin) / fps);
        fr = Math.round(frames - hr * frHour - mn * frMin - sc * fps);
    }
    if (CHT) {
        timeList = [hr,mn,sc,fr];
        chtTimeList = ['時','分','秒','格'];
        var result = '';
        for (i = 0; i < 4; i++){
            if (timeList[i] == 0) continue;
            result += String(timeList[i]) + chtTimeList[i];
            i += 1;
        }
        return result;
    } else {
        return ("00" + hr).slice(-2) + spacer + ("00" + mn).slice(-2) + spacer + ("00" + sc).slice(-2) + spacer2 + ("00" + fr).slice(-2);
    }
}

function getOutputFile(fname){
    var path = ''
    if(app.project.file !== null){
        var path = String(app.project.file.parent);
    }
    return new File(path + '/' + fname + ".csv").saveDlg(["Export CSV"],["*.csv"]);
  }

function exportCSV (curComp) {
    var outputFile = getOutputFile(curComp.name);
    if (outputFile === null) return;

    var fps = curComp.frameRate;
    var dropFrame = curComp.dropFrame;
    var layers = curComp.layers;
    setTimeDisplayTypeTo('frame');

    firstRow = [
        "NO",
        "段落",
        "time in",
        "time out",
        "秒數",
        "frame in",
        "frame out",
        "cut duration",
    ]
    outputFile.open('w');
    outputFile.writeln('"' + firstRow.join('","') + '"');

    for (var i = 1, l = layers.length; i <= l; i++) {
        var frameIn = timeToCurrentFormat(layers[i].inPoint,fps)-0;
        var frameOut = timeToCurrentFormat(layers[i].outPoint,fps)-1;
        var frameDuration = frameOut - frameIn + 1;
        var chtFrameDuration = framesToTC(frameDuration, fps, dropFrame, true);
        var timeIn = framesToTC(frameIn, fps, dropFrame, false);
        var timeOut = framesToTC(frameOut, fps, dropFrame, false);
        row = [layers[i].index, layers[i].name, timeIn, timeOut, chtFrameDuration, frameIn, frameOut, frameDuration];
        outputFile.writeln('"' + row.join('","') + '"');
    }
    outputFile.close();
    setTimeDisplayTypeTo('orig');
    if (outputFile.exists) {
        alert('Export Sucess!');
        return;
    }
    alert('Export Failed!');
    return;
}

function showUI() {
    /*
    Code for Import https://scriptui.joonas.me — (Triple click to select): 
    {"activeId":2,"items":{"item-0":{"id":0,"type":"Dialog","parentId":false,"style":{"enabled":true,"varName":null,"windowType":"Dialog","creationProps":{"su1PanelCoordinates":false,"maximizeButton":false,"minimizeButton":false,"independent":false,"closeButton":true,"borderless":false,"resizeable":false},"text":"Export layer info to CSV","preferredSize":[200,0],"margins":16,"orientation":"column","spacing":10,"alignChildren":["center","top"]}},"item-2":{"id":2,"type":"Button","parentId":0,"style":{"enabled":true,"varName":null,"text":"About","justify":"center","preferredSize":[0,0],"alignment":null,"helpTip":null}},"item-3":{"id":3,"type":"Button","parentId":0,"style":{"enabled":true,"varName":null,"text":"Export","justify":"center","preferredSize":[0,0],"alignment":null,"helpTip":null}}},"order":[0,2,3],"settings":{"importJSON":true,"indentSize":false,"cepExport":false,"includeCSSJS":true,"showDialog":true,"functionWrapper":false,"afterEffectsDockable":false,"itemReferenceList":"None"}}
    */ 
    if (!curComp || !(curComp instanceof CompItem)) {
        alert('Select the current comp item first.');
        return;
    }
    var dialog = new Window("dialog"); 
        dialog.text = "Export layer info to CSV"; 
        dialog.preferredSize.width = 200; 
        dialog.orientation = "column"; 
        dialog.alignChildren = ["center","top"]; 
        dialog.spacing = 10; 
        dialog.margins = 16; 

    var button1 = dialog.add("button", undefined, undefined, {name: "button1"}); 
        button1.text = "About"; 
        button1.onClick = function () {
            alert('Author:Wei-Hsiang Chen');
        };

    var button2 = dialog.add("button", undefined, undefined, {name: "button2"}); 
        button2.text = "Export";
        button2.onClick = function () {
            exportCSV(curComp);
        };
        
    dialog.show();
}

var curComp = app.project.activeItem;
if (writingFilesEnabled()){
    showUI();
}
