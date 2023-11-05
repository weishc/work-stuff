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
