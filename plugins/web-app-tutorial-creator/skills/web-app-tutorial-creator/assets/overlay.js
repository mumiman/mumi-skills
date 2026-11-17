/* WATC v2. Native DOM only. Never evaluate spec strings or mutate application controls. */
(function (global) {
  'use strict';
  if (global.WATC && typeof global.WATC.destroy === 'function') global.WATC.destroy();
  const LABELS = {
    en: {next:'Next',back:'Back',skip:'Skip',done:'Finish',close:'Close',retry:'Retry',focus:'Go to target',waiting:'Waiting for this step. Open the required page or control.',missing:'Target unavailable. Open the required page/control, then retry or continue.',step:'Step',of:'of',expected:'Expected result',empty:'No tutorial steps configured.'},
    th: {next:'ถัดไป',back:'ย้อนกลับ',skip:'ข้าม',done:'เสร็จสิ้น',close:'ปิด',retry:'ลองอีกครั้ง',focus:'ไปยังจุดที่อธิบาย',waiting:'กำลังรอ กรุณาเปิดหน้าหรือส่วนที่เกี่ยวข้อง',missing:'ยังไม่พบจุดที่อธิบาย เปิดหน้าหรือส่วนที่เกี่ยวข้อง แล้วลองอีกครั้งหรือไปขั้นตอนถัดไป',step:'ขั้นตอนที่',of:'จาก',expected:'ผลที่คาดหวัง',empty:'ยังไม่มีขั้นตอน'}
  };
  let current = null;
  const visible = el => {
    if (!el || !el.isConnected || !el.getClientRects().length) return false;
    for (let node = el; node instanceof Element; node = node.parentElement) {
      const css = getComputedStyle(node);
      if (node.inert || node.getAttribute('aria-hidden') === 'true' || css.display === 'none' || css.visibility === 'hidden' || css.visibility === 'collapse' || Number(css.opacity) === 0) return false;
    }
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };
  const enabled = element => !element.disabled && element.getAttribute('aria-disabled') !== 'true' && !element.matches(':disabled');
  function resolve(target = {}) {
    const candidates = [target.selector, ...(target.fallbacks || [])].filter(Boolean);
    const issues = [];
    for (const selector of candidates) {
      try {
        const list = document.querySelectorAll(selector);
        if (Number.isInteger(target.index)) {
          if (list[target.index] && visible(list[target.index]) && (target.enabled === false || enabled(list[target.index]))) return {element:list[target.index], selector, count:list.length, issues:['indexed-selector']};
        } else if (list.length === 1 && visible(list[0]) && (target.enabled === false || enabled(list[0]))) {
          return {element:list[0], selector, count:1, issues};
        }
        issues.push(list.length > 1 ? 'ambiguous' : list.length ? (visible(list[0]) ? 'disabled' : 'hidden') : 'missing');
      } catch (_) { issues.push('invalid-selector'); }
    }
    return {element:null, issues, count:0};
  }
  function routeMatches(route) {
    if (!route) return true;
    if (!route.startsWith('/')) return false;
    const actual = location.pathname + location.search + location.hash;
    return actual === route || (!/[?#]/.test(route) && location.pathname === route);
  }
  function conditionReady(condition) {
    if (!condition) return true;
    try {
      const nodes = document.querySelectorAll(condition.selector);
      if (condition.state === 'hidden') return !Array.from(nodes).some(visible);
      return nodes.length === 1 && (condition.state === 'attached' || visible(nodes[0]));
    } catch (_) { return false; }
  }
  function create(spec, options = {}) {
    if (current) current.destroy();
    if (!spec || !Array.isArray(spec.steps) || spec.steps.length === 0) throw new Error('WATC needs a non-empty normalized spec');
    const words = {...LABELS[spec.language === 'th' ? 'th' : 'en'], ...(spec.controls || {})};
    let index = 0, state = 'idle', host, shadow, tip, marker, heading, text, notice, meta, expected;
    let back, next, retry, focusButton, controller, observer, resizeObserver, interval, raf = 0;
    let disposed = false, active = false, target = null, deadline = 0, lastURL = '', priorFocus, targetFocus = null;
    let findings = [], lastState = '', lastTarget = null;
    const local = (step, key) => (spec.locales?.[spec.language]?.[step.i18n?.[key]] ?? step[key] ?? '');
    const add = (tag, className, parent, content) => {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (content != null) node.textContent = content;
      parent.appendChild(node); return node;
    };
    function restoreTarget() {
      if (targetFocus && targetFocus.element.isConnected && targetFocus.element.getAttribute('tabindex') === '-1') {
        if (targetFocus.old === null) targetFocus.element.removeAttribute('tabindex');
        else targetFocus.element.setAttribute('tabindex', targetFocus.old);
      }
      targetFocus = null;
    }
    function focusTarget() {
      if (!target || !enabled(target)) return;
      restoreTarget();
      if (!target.matches('button,a[href],input,select,textarea,[tabindex]')) {
        targetFocus = {element:target, old:target.getAttribute('tabindex')}; target.setAttribute('tabindex','-1');
      }
      target.focus({preventScroll:true});
    }
    function build() {
      host = document.createElement('div'); host.dataset.watcRoot = '';
      shadow = host.attachShadow({mode:'open'});
      if (options.styleUrl) {
        const url = new URL(options.styleUrl, location.href);
        if (url.origin !== location.origin) throw new Error('WATC stylesheet must be same-origin');
        const link = add('link','',shadow); link.rel='stylesheet'; link.href=url.href;
        link.addEventListener('load', schedule, {signal:controller.signal});
      } else {
        if (!options.css) throw new Error('Provide css or a same-origin styleUrl');
        const style = add('style','',shadow); if (options.nonce) style.nonce=options.nonce; style.textContent=options.css;
      }
      const theme = spec.render || {};
      for (const [key,value] of Object.entries({accent:theme.accent,font:theme.font,radius:theme.radius == null ? null : theme.radius+'px',dim:theme.dim,border:theme.border == null ? null : theme.border+'px'})) {
        if (value != null) host.style.setProperty('--watc-'+key, String(value));
      }
      marker = add('div','highlight',shadow); marker.setAttribute('aria-hidden','true'); marker.hidden=true;
      tip = add('section','tip',shadow); tip.setAttribute('role','dialog'); tip.setAttribute('aria-modal','false'); tip.setAttribute('aria-labelledby','watc-heading'); tip.setAttribute('aria-describedby','watc-instruction'); tip.tabIndex=-1; tip.lang=spec.language;
      meta = add('div','meta',tip); meta.setAttribute('aria-live','polite'); meta.setAttribute('aria-atomic','true');
      heading = add('h2','',tip); heading.id='watc-heading';
      text = add('p','',tip); text.id='watc-instruction';
      expected = add('p','',tip);
      notice = add('p','notice',tip); notice.setAttribute('role','status');
      const actions = add('div','actions',tip);
      const button = (name, callback, primary=false) => {
        const el = add('button',primary?'primary':'',actions,words[name]); el.type='button'; el.dataset.action=name;
        el.addEventListener('click',callback,{signal:controller.signal}); return el;
      };
      button('close',()=>stop('idle')); button('skip',()=>advance());
      back=button('back',()=>goTo(index-1)); retry=button('retry',()=>goTo(index));
      focusButton=button('focus',focusTarget); next=button('next',advance,true);
      document.body.appendChild(host);
      // Manual popover joins the top layer without trapping focus or blocking the app.
      if (typeof host.showPopover === 'function') {
        host.setAttribute('popover','manual'); host.showPopover();
      }
    }
    function modalContext() {
      try { return Array.from(document.querySelectorAll('dialog:modal')).at(-1) || null; }
      catch (_) { return Array.from(document.querySelectorAll('dialog[open]')).at(-1) || null; }
    }
    function mountContext() {
      const modal=modalContext(), parent=modal || document.body;
      if (host.parentElement !== parent) {
        const focused=shadow.activeElement;
        parent.appendChild(host);
        // Moving a popover can close it. Reopen only our own manual popover.
        if (typeof host.showPopover === 'function') {
          try { host.showPopover(); } catch (_) { /* already open or unsupported state */ }
        }
        if (focused?.isConnected) focused.focus({preventScroll:true});
      }
      return modal;
    }
    function schedule() { if (active && !raf) raf=requestAnimationFrame(()=>{raf=0; refresh();}); }
    function clippedRect(element) {
      let r=element.getBoundingClientRect();
      let left=Math.max(0,r.left), top=Math.max(0,r.top), right=Math.min(innerWidth,r.right), bottom=Math.min(innerHeight,r.bottom);
      for (let parent=element.parentElement; parent; parent=parent.parentElement) {
        const css=getComputedStyle(parent), p=parent.getBoundingClientRect();
        if (/(auto|scroll|hidden|clip)/.test(css.overflowX)) {left=Math.max(left,p.left);right=Math.min(right,p.right);}
        if (/(auto|scroll|hidden|clip)/.test(css.overflowY)) {top=Math.max(top,p.top);bottom=Math.min(bottom,p.bottom);}
      }
      return {left,top,right,bottom,width:Math.max(0,right-left),height:Math.max(0,bottom-top)};
    }
    function place() {
      if (!tip) return;
      const view=global.visualViewport;
      const vx=view?.offsetLeft || 0, vy=view?.offsetTop || 0;
      const vw=view?.width || innerWidth, vh=view?.height || innerHeight;
      tip.style.width=Math.min(360,Math.max(120,vw-24))+'px'; tip.style.maxHeight=Math.max(60,vh-24)+'px';
      const box=tip.getBoundingClientRect();
      let x=vx+(vw-box.width)/2, y=vy+(vh-box.height)/2;
      marker.hidden=true;
      if (target) {
        const r=clippedRect(target);
        if (r.width && r.height) {
          marker.hidden=false;
          Object.assign(marker.style,{left:(r.left-3)+'px',top:(r.top-3)+'px',width:(r.width+6)+'px',height:(r.height+6)+'px'});
          const places={bottom:[r.left,r.bottom+12],top:[r.left,r.top-box.height-12],right:[r.right+12,r.top],left:[r.left-box.width-12,r.top]};
          const requested=spec.steps[index].overlay?.placement || 'auto';
          const order=[requested,...['bottom','top','right','left']].filter((v,i,a)=>places[v] && a.indexOf(v)===i);
          const fit=order.find(p=>{const [px,py]=places[p]; return px>=vx+8 && py>=vy+8 && px+box.width<=vx+vw-8 && py+box.height<=vy+vh-8;});
          if (fit) [x,y]=places[fit];
          else {x=vx+12; y= r.top-vy > vy+vh-r.bottom ? vy+12 : vy+vh-box.height-12;}
        }
      }
      tip.style.left=Math.max(vx+8,Math.min(x,vx+vw-box.width-8))+'px';
      tip.style.top=Math.max(vy+8,Math.min(y,vy+vh-box.height-8))+'px';
    }
    function refresh() {
      if (!active) return;
      const modal=mountContext();
      const step=spec.steps[index], rule=step.target || {};
      if (lastURL !== location.href) {lastURL=location.href; deadline=performance.now()+(rule.timeout_ms ?? 5000); lastTarget=null;}
      const resolved=routeMatches(rule.route) && conditionReady(rule.wait_for) ? resolve(rule) : {element:null,issues:['route-or-condition']};
      if (modal && resolved.element && !modal.contains(resolved.element)) {resolved.element=null; resolved.issues.push('outside-modal');}
      findings=resolved.issues; target=resolved.element;
      state=target?'active':performance.now()<deadline?'waiting':'missing';
      if (target && target !== lastTarget) {
        restoreTarget();
        target.scrollIntoView({behavior:'instant',block:'center',inline:'nearest'});
        lastTarget=target;
        resizeObserver?.disconnect(); resizeObserver?.observe(target); resizeObserver?.observe(tip);
      }
      if (lastState !== state) {
        notice.hidden=state==='active'; notice.textContent=state==='waiting'?words.waiting:words.missing;
        retry.hidden=state!=='missing'; lastState=state;
      }
      focusButton.hidden=!target || !enabled(target);
      place();
    }
    function goTo(value) {
      if (!active || !Number.isInteger(value) || value<0 || value>=spec.steps.length) return;
      restoreTarget(); index=value; target=null; lastTarget=null; lastState='';
      const step=spec.steps[index]; deadline=performance.now()+(step.target?.timeout_ms ?? 5000); lastURL=location.href;
      heading.textContent=local(step,'title') || spec.title;
      text.textContent=step.overlay?.instruction || local(step,'instruction');
      const outcome=local(step,'expected_result'); expected.hidden=!outcome; expected.textContent=outcome?words.expected+': '+outcome:'';
      meta.textContent=words.step+' '+(index+1)+' '+words.of+' '+spec.steps.length;
      back.disabled=index===0; next.textContent=index===spec.steps.length-1?words.done:words.next;
      refresh(); tip.focus({preventScroll:true});
    }
    function advance() { if (index===spec.steps.length-1) stop('finished'); else goTo(index+1); }
    function start() {
      if (disposed) throw new Error('WATC instance destroyed; configure a new instance');
      if (active) stop('idle');
      priorFocus=document.activeElement; controller=new AbortController(); active=true;
      try { build(); } catch(error) {stop('idle'); throw error;}
      const signal=controller.signal;
      global.addEventListener('resize',schedule,{signal}); document.addEventListener('scroll',schedule,{capture:true,passive:true,signal});
      global.visualViewport?.addEventListener('resize',schedule,{signal}); global.visualViewport?.addEventListener('scroll',schedule,{signal});
      global.addEventListener('popstate',schedule,{signal}); global.addEventListener('hashchange',schedule,{signal});
      document.addEventListener('keydown', event=>{
        if (event.key==='F6') {event.preventDefault(); tip.focus({preventScroll:true});}
        if (event.key==='Escape' && (event.composedPath().includes(host) || document.activeElement===target)) {event.preventDefault(); stop('idle');}
      },{signal});
      observer=new MutationObserver(schedule); observer.observe(document.body,{subtree:true,childList:true,attributes:true,attributeFilter:['class','style','hidden','open','aria-hidden','id','data-testid','data-tour']});
      if (global.ResizeObserver) resizeObserver=new ResizeObserver(schedule);
      // Handles pushState and CSS/layout changes without monkey-patching the host router.
      interval=setInterval(schedule,200);
      goTo(0);
    }
    function stop(nextState='idle') {
      if (disposed) return;
      const wasActive=active;
      active=false; controller?.abort(); observer?.disconnect(); resizeObserver?.disconnect(); clearInterval(interval); cancelAnimationFrame(raf); raf=0;
      restoreTarget(); host?.remove(); host=null; target=null; state=nextState;
      if (wasActive && priorFocus?.isConnected) priorFocus.focus({preventScroll:true});
      priorFocus=null;
    }
    const api={start,stop:()=>stop('idle'),goTo,destroy:()=>{stop('destroyed');disposed=true;},getState:()=>({state,index,id:spec.steps[index]?.id,issues:[...findings]}),inspect:()=>spec.steps.map(step=>({id:step.id,routeMatches:routeMatches(step.target?.route),...(()=>{const result=resolve(step.target);return {count:result.count,selector:result.selector || null,visible:!!result.element,issues:result.issues};})()}))};
    current=api; return api;
  }
  global.WATC={create,configure:create,start:()=>current?.start(),stop:()=>current?.stop(),goTo:i=>current?.goTo(i),destroy:()=>current?.destroy(),getState:()=>current?.getState(),inspect:()=>current?.inspect()};
})(window);
