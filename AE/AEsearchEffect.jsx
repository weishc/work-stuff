function search(searchFXname) {
    edittext2.text = "";
    var compNum = app.project.numItems;
    var sR = "";
    for (var compIdx = 1; compIdx <= compNum; compIdx++) {
        var curComp = app.project.item(compIdx);
        if (curComp.numLayers == undefined) {
            continue;
        }
        for (var layIdx = 1; layIdx <= curComp.numLayers; layIdx++) {
            curLayer = curComp.layer(layIdx);
            var fxs = curLayer.property("Effects");
            if (fxs == null || fxs.numProperties == 0) {
                continue;
            }
            for (var fxIdx = 1; fxIdx <= fxs.numProperties; fxIdx++) {
                var fxName = fxs.property(fxIdx).name;
                var regex = new RegExp(searchFXname, "i");
                if (fxName.match(regex)) {
                    sR = sR.concat(curComp.name, ' --> ', curLayer.name, ' --> ', fxName, '\r');
                }
            }
        }
    }
    if (sR == "") {
        alert('Found nothing.');
    }
    else {
        edittext2.text = sR;
        alert('Done.');
    }
}

var dialog = new Window("dialog"); 
    dialog.text = "Where's my effect?"; 
    dialog.orientation = "column"; 
    dialog.alignChildren = ["center","top"]; 
    dialog.spacing = 10; 
    dialog.margins = 16; 

var statictext1 = dialog.add("statictext", undefined, undefined, {name: "statictext1"}); 
    statictext1.text = "Effect's name:"; 

var edittext1 = dialog.add('edittext {properties: {name: "edittext1"}}'); 
    edittext1.text = ""; 
    edittext1.preferredSize.width = 200; 

var edittext2 = dialog.add('edittext {size: [500,100], properties: {name: "edittext2", readonly: true, multiline: true}}'); 
    edittext2.text = ""; 

var button1 = dialog.add("button", undefined, undefined, {name: "button1"}); 
    button1.text = "Search";
    button1.onClick = function () {
        search(edittext1.text);
    };

dialog.show();

