function frames_to_TC(frames, fps) {
    var h = Math.floor(frames / Math.pow(fps, 60));
    var m = Math.floor(frames / (fps * 60)) % 60;
    var s = Math.floor((frames % (fps * 60)) / fps);
    var f = Math.floor(frames % (fps * 60) % fps);
    return ("00" + h).slice(-2) + ":" + ("00" + m).slice(-2) + ":" + ("00" + s).slice(-2) + ":" + ("00" + f).slice(-2);
}
// Example usage:
var frames = 108000; // Replace with your frames value
var fps = 29.97; // Replace with your frames per second value
var timecode = frames_to_TC(frames, fps);
alert(timecode);

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
"Allow scripts to write files and access network".  \
You can find it in Edit->Preferences->Scripting & Experssion.' );
        ( version16Check ) ? app.executeCommand( 3131 ): app.executeCommand( 2359 );
    }
    return ( securitySetting === 1 );
}
