/* Read-only collector. Run only through a browser tool that permits DOM evaluation.
   Does not read input values, cookies, storage, script text or query parameters. */
(() => {
  const visible = element => {
    const style = getComputedStyle(element), rect = element.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0 && style.display !== 'none' && style.visibility !== 'hidden';
  };
  const escapeValue = value => '"' + value.replace(/\\/g,'\\\\').replace(/"/g,'\\"').replace(/\n/g,'\\a ') + '"';
  const controls = Array.from(document.querySelectorAll('button,a[href],input:not([type=hidden]),select,textarea,[role=button],[role=tab],[role=dialog]')).filter(visible).slice(0,200).map(element => {
    const candidates=[];
    for (const attribute of ['data-tour','data-testid','data-test','id']) {
      const value=element.getAttribute(attribute);
      if (value) candidates.push(attribute==='id'?'#'+CSS.escape(value):'['+attribute+'='+escapeValue(value)+']');
    }
    if (element.getAttribute('name')) candidates.push(element.tagName.toLowerCase()+'[name='+escapeValue(element.getAttribute('name'))+']');
    const selectors=candidates.map(selector=>({selector,count:document.querySelectorAll(selector).length}));
    const rect=element.getBoundingClientRect();
    const label=(element.getAttribute('aria-label') || (element.matches('input,textarea,select') ? Array.from(element.labels || []).map(x=>x.textContent).join(' ') : element.textContent) || '').trim().slice(0,120);
    return {tag:element.tagName.toLowerCase(),role:element.getAttribute('role'),label,selectors,rect:{x:rect.x,y:rect.y,width:rect.width,height:rect.height},coordinate_space:'viewport-css-pixels',disabled:!!element.disabled,potential_sensitive: /@|\d{8,}|patient|ผู้ป่วย|password|รหัสผ่าน/i.test(label)};
  });
  return {kind:'browser',route:location.pathname,viewport:{width:innerWidth,height:innerHeight,devicePixelRatio},controls,truncated:controls.length===200,limitations:['Snapshot of current state only; no field values captured.','Coordinates are CSS pixels, not screenshot pixels.','Control existence does not establish workflow or outcome.']};
})();
