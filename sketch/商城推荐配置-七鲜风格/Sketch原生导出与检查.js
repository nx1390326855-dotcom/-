/* Run inside Sketch: Plugins > Run Script. Select the delivered .sketch file.
 * Official API: Document.open, document.save, sketch.export.
 * Writes an independent copy and native previews to Desktop/商城推荐配置-七鲜风格.
 * The original document is preserved.
 */
var onRun = function () {
  const sketch = require('sketch');
  const dom = require('sketch/dom');
  const fm = NSFileManager.defaultManager();
  const panel = NSOpenPanel.openPanel();
  panel.setCanChooseDirectories(false);
  panel.setAllowsMultipleSelection(false);
  panel.setAllowedFileTypes(['sketch']);
  panel.setMessage('选择交付的「商城首页推荐配置-七鲜风格.sketch」');
  if (panel.runModal() !== NSModalResponseOK) return;
  const file = String(panel.URL().path());
  const output = String(NSHomeDirectory()) + '/Desktop/商城推荐配置-七鲜风格';
  const stamp = Date.now();
  const write = (path, value) => {
    if (!NSString.stringWithString(String(value)).writeToFile_atomically_encoding_error(path, true, NSUTF8StringEncoding, null)) throw new Error('无法写入：' + path);
  };
  if (!fm.createDirectoryAtPath_withIntermediateDirectories_attributes_error(output, true, null, null)) throw new Error('无法创建桌面输出目录');
  const document = dom.Document.open(file);
  const boards = [];
  const counts = {};
  const errors = [];
  let photoCount = 0;
  const walk = layer => {
    counts[layer.type] = (counts[layer.type] || 0) + 1;
    if (layer.type === 'Artboard') {
      boards.push(layer);
      if (Math.abs(layer.frame.width - 390) > .1 || Math.abs(layer.frame.height - 844) > .1) errors.push(layer.name + ' 画板尺寸异常');
    }
    if (layer.type === 'Image') {
      photoCount++;
      if (layer.frame.width > 160 || layer.frame.height > 160) errors.push(layer.name + ' 不应是整页图片');
    }
    if (layer.type === 'Text' && !layer.text) errors.push(layer.name + ' 文字为空');
    if (layer.layers) layer.layers.forEach(walk);
  };
  document.pages.forEach(walk);
  if (boards.length !== 10) errors.push('预期 10 个画板，实际 ' + boards.length);
  if (errors.length) throw new Error(errors.join('\n'));
  const target = output + '/商城首页推荐配置-七鲜风格-本机保存-' + stamp + '.sketch';
  document.save(target, {saveMode: 'SaveAs'}, error => {
    if (error) { write(output + '/保存失败-' + stamp + '.txt', error); return; }
    try {
      const pngPath = output + '/Sketch原生预览-' + stamp;
      sketch.export(boards, {output: pngPath, formats: 'png', scales: '3', overwriting: false});
      write(output + '/本机验证结果-' + stamp + '.json', JSON.stringify({source: file, saved: target, previews: pngPath, sketchVersion: sketch.version.sketch, artboards: boards.length, layers: counts, productPhotos: photoCount, verifiedBy: 'Sketch official JavaScript API', checkedAt: new Date().toISOString()}, null, 2));
      sketch.UI.message('已保存 Sketch 副本并原生导出 10 个画板');
    } catch (e) { write(output + '/导出失败-' + stamp + '.txt', String(e)); }
  });
};
if (typeof module !== 'undefined') module.exports = {onRun: onRun};
// Running the file directly in Sketch's Run Script window also executes it.
if (typeof context !== 'undefined') onRun(context);
