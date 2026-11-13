/* Extracted source handlers; demo-runtime owns the lifecycle. */
window.VibeDemos.register('ui',env=>{
const {scope,document,window,matchMedia,setTimeout,clearTimeout,setInterval,clearInterval,requestAnimationFrame,cancelAnimationFrame,performance,animate,toast}=env;
function demoSearch(el){
    const value=el.closest('.searchbox').querySelector('input').value.trim();
    toast(value?'搜索（演示）：'+value:'请输入搜索词');
  }
  function demoRegister(){
    const fields=document.querySelectorAll('#c-form .canvas input');
    toast([...fields].every(x=>x.value.trim())?'模拟提交完成，未创建账号':'请先填写用户名和密码（演示）');
  }
  let modalReturnFocus;
  function openModal(){
    modalReturnFocus=document.activeElement;
    const modal=document.getElementById('modal');
    modal.style.display='flex';
    modal.querySelector('button').focus();
  }
  function closeModal(){
    const modal=document.getElementById('modal');
    if(modal.style.display!=='flex') return;
    modal.style.display='none';
    if(modalReturnFocus&&modalReturnFocus.isConnected) modalReturnFocus.focus();
  }
  document.getElementById('modal')?.addEventListener('keydown',e=>{
    if(e.key!=='Tab') return;
    const buttons=[...e.currentTarget.querySelectorAll('button')];
    if(e.shiftKey&&document.activeElement===buttons[0]){e.preventDefault();buttons.at(-1).focus();}
    else if(!e.shiftKey&&document.activeElement===buttons.at(-1)){e.preventDefault();buttons[0].focus();}
  });
  document.getElementById('modal')?.addEventListener('click',e=>{ if(e.target.id==='modal') closeModal(); });

  /* ---- 演示交互 ---- */
  function switchTab(el,idx){
    if(el.disabled)return;
    el.parentNode.querySelectorAll('.tab').forEach(t=>{
      const current=t===el;
      t.classList.toggle('active',current);
      t.setAttribute('aria-selected',String(current));
      t.tabIndex=current?0:-1;
    });
    const panel=document.getElementById('tp');
    panel.textContent=['这是「简介」的内容区域。','这是「评价」的内容区域。','这是「帮助」的内容区域。'][idx];
    panel.setAttribute('aria-labelledby',el.id);
  }
  document.querySelector('#c-tabs [role="tablist"]')?.addEventListener('keydown',e=>{
    if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key)) return;
    e.preventDefault();
    const tabs=[...e.currentTarget.querySelectorAll('[role="tab"]:not(:disabled)')];
    const i=tabs.indexOf(document.activeElement);
    const next=e.key==='Home'?0:e.key==='End'?tabs.length-1:(i+(e.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;
    switchTab(tabs[next],Number(tabs[next].dataset.arg)); tabs[next].focus();
  });
  function toggleAcc(head){
    const item=head.parentNode;
    const wasOpen=item.classList.contains('open');
    item.parentNode.querySelectorAll('.acc-item').forEach(i=>{
      i.classList.remove('open');
      i.querySelector('.acc-head').setAttribute('aria-expanded','false');
      i.querySelector('.acc-body').hidden=true;
    });
    if(!wasOpen){item.classList.add('open');head.setAttribute('aria-expanded','true');item.querySelector('.acc-body').hidden=false;}
  }
  function stepNum(d){
    const n=document.getElementById('num');
    let v=parseInt(n.value||0,10)+d;
    if(v<0)v=0;
    n.value=v;
  }
  document.querySelectorAll('input[type=color]')[0]?.addEventListener('input',e=>{
    document.getElementById('hexc').textContent=e.target.value;
  });
  const sts=document.querySelectorAll('#stars .st');
  function rate(idx){ sts.forEach((s,i)=>{s.classList.toggle('on',i<=idx);s.setAttribute('aria-pressed',String(i===idx));}); }
  sts.forEach((s,i)=>s.addEventListener('click',()=>rate(i)));
  const dz=document.getElementById('dz'), fi=document.getElementById('filei');
  if(dz&&fi){dz.addEventListener('keydown',e=>{
    if(e.key==='Enter'||e.key===' '){e.preventDefault();fi.click();}
  });
  fi.addEventListener('change',()=>{
    if(fi.files.length){
      document.getElementById('dz-text').textContent='已选择：'+fi.files[0].name+'（未上传；点击可重选）';
      toast('已选择文件，未上传：'+fi.files[0].name);
    }
  });
  dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('drag');});
  dz.addEventListener('dragleave',()=>dz.classList.remove('drag'));
  dz.addEventListener('drop',e=>{
    e.preventDefault();dz.classList.remove('drag');
    if(!e.dataTransfer.files.length) return;
    try{
      fi.files=e.dataTransfer.files;
      if(fi.files.length) fi.dispatchEvent(new Event('change',{bubbles:true}));
      else toast('无法读取文件，请点击选择');
    }catch(_){toast('此浏览器无法接收拖入文件，请点击选择');}
  });
  }
  function toggleDD(e){ e.stopPropagation(); document.getElementById('dd').classList.toggle('open'); }
  function pickDD(el){ toast('点击了「'+el.textContent.trim()+'」'); document.getElementById('dd')?.classList.remove('open'); }
  document.addEventListener('click',(e)=>{ if(e.target.closest('[data-cmd]'))return; document.getElementById('dd')?.classList.remove('open'); });
  function closePopover(){if(!document.getElementById('popover-box'))return;
    document.getElementById('popover-box').hidden=true;
    document.getElementById('popover-trigger').setAttribute('aria-expanded','false');
  }
  function toggleInfoPopover(e){
    e.stopPropagation();
    const box=document.getElementById('popover-box');
    box.hidden=!box.hidden;
    document.getElementById('popover-trigger').setAttribute('aria-expanded',String(!box.hidden));
  }
  document.addEventListener('click',e=>{if(!e.target.closest('.popover-demo')) closePopover();});
  function openDrawer(){ document.getElementById('dmask').classList.add('show'); }
  function closeDrawer(){ document.getElementById('dmask').classList.remove('show'); }

  /* ---- 轮播 ---- */
  (function(){
    const track=document.getElementById('carTrack');if(!track)return;
    const carousel=track.closest('.carousel'), pause=document.getElementById('carPause');
    const dots=[...document.querySelectorAll('#carDots button')];
    const n=dots.length; let i=0, timer, userPaused=false;
    const reduced=matchMedia('(prefers-reduced-motion: reduce)');
    function go(k){ i=(k+n)%n; track.style.transform='translateX(-'+(i*100)+'%)'; dots.forEach((d,j)=>{d.classList.toggle('on',j===i);d.setAttribute('aria-current',String(j===i));}); }
    function auto(){
      clearInterval(timer);
      if(!userPaused&&!reduced.matches&&!carousel.matches(':hover')&&!carousel.contains(document.activeElement)&&!document.hidden)
        timer=setInterval(()=>go(i+1),3500);
    }
    document.getElementById('carPrev').onclick=()=>{go(i-1);auto();};
    document.getElementById('carNext').onclick=()=>{go(i+1);auto();};
    dots.forEach((d,j)=>d.onclick=()=>{go(j);auto();});
    pause.onclick=()=>{userPaused=!userPaused;pause.setAttribute('aria-pressed',String(userPaused));pause.setAttribute('aria-label',userPaused?'继续自动轮播':'暂停自动轮播');pause.textContent=userPaused?'继续':'暂停';auto();};
    carousel.addEventListener('mouseenter',()=>clearInterval(timer));
    carousel.addEventListener('mouseleave',auto);
    carousel.addEventListener('focusin',()=>clearInterval(timer));
    carousel.addEventListener('focusout',()=>setTimeout(auto,0));
    document.addEventListener('visibilitychange',auto);
    reduced.addEventListener('change',auto);
    auto();
  })();

  /* ---- 步骤条 ---- */
  function setStep(k){
    const items=[...document.querySelectorAll('#stepsBox .step')];
    items.forEach((s,j)=>{ s.classList.toggle('cur',j===k); s.classList.toggle('done',j<k); s.setAttribute('aria-current',j===k?'step':'false'); });
  }

  /* ---- 通知角标：点击清除 ---- */
  document.querySelectorAll('.bdg').forEach(b=>{
    b.addEventListener('click',()=>{ const m=b.querySelector('.dot,.num'); if(m){m.remove();b.setAttribute('aria-label','角标已清除');toast('已读 ✓');} });
  });

  const catName={input:'输入',feedback:'反馈',nav:'导航',display:'展示'};
/* ---- 命令面板（页面自己的快速跳转） ---- */
  const cmdk=document.getElementById('cmdk'), cmdkInput=document.getElementById('cmdkInput'), cmdkList=document.getElementById('cmdkList');
  const cmds=cmdk?JSON.parse(cmdk.dataset.demoCommands||'[]'):[];
  let sel=0, filtered=[...cmds];
  function jumpTo(command){location.assign(command.href);}  function renderCmdk(q){
    q=(q||'').trim().toLowerCase();
    filtered=!q?cmds:cmds.filter(c=>c.name.toLowerCase().includes(q)||c.keys.includes(q));
    sel=0;
    cmdkList.textContent='';
    filtered.slice(0,8).forEach((c,j)=>{
      const d=document.createElement('div'); d.className='cmdk-item'+(j===0?' sel':'');
      const nm=document.createElement('span'); nm.textContent='前往 · '+c.name;
      const ct=document.createElement('span'); ct.className='cat-sm'; ct.textContent=(catName[c.cat]||'');
      d.append(nm,ct);
      d.addEventListener('click',()=>{ jumpTo(c); closeCmdk(); });
      cmdkList.appendChild(d);
    });
    if(!filtered.length){ const e=document.createElement('div'); e.className='cmdk-empty'; e.textContent='没有匹配的组件'; cmdkList.appendChild(e); }
  }
  let cmdkFocusBefore=null;
  function openCmdk(){ cmdkFocusBefore=document.activeElement; cmdk.classList.add('show'); cmdkInput.value=''; renderCmdk(''); cmdkInput.focus(); }
  function closeCmdk(){ if(!cmdk||!cmdk.classList.contains('show'))return; cmdk.classList.remove('show'); if(cmdkFocusBefore?.isConnected)cmdkFocusBefore.focus(); cmdkFocusBefore=null; }
  cmdkInput?.addEventListener('input',()=>renderCmdk(cmdkInput.value));
  cmdkInput?.addEventListener('keydown',e=>{
    const items=[...cmdkList.querySelectorAll('.cmdk-item')];
    if(e.key==='Escape'){ closeCmdk(); return; }
    if(e.key==='ArrowDown'){ e.preventDefault(); sel=Math.min(sel+1,items.length-1); }
    else if(e.key==='ArrowUp'){ e.preventDefault(); sel=Math.max(sel-1,0); }
    else if(e.key==='Enter'){ e.preventDefault(); if(filtered.slice(0,8)[sel]){ jumpTo(filtered[sel]); closeCmdk(); } return; }
    else return;
    items.forEach((it,j)=>it.classList.toggle('sel',j===sel));
  });
  cmdk?.addEventListener('keydown',e=>{if(e.key==='Tab'){e.preventDefault();cmdkInput.focus();}});
  cmdk?.addEventListener('click',e=>{ if(e.target===cmdk) closeCmdk(); });

  /* ---- 密码强度 ---- */
  (function(){
    const pw=document.getElementById('pwInput');
    if(!pw) return;
    const demo=pw.closest('.pw-demo'), hint=demo.querySelector('.pw-hint');
    const hints=['至少 8 位，混合字母、数字与符号。','强度：弱 —— 再加些长度，或混合字母与数字。','强度：中 —— 建议再混入符号。','强度：强，可以放心使用。','强度：很强，非常稳。'];
    pw.addEventListener('input',()=>{
      const v=pw.value;
      let score=0;
      if(v.length>=8)score++;
      if(/[a-zA-Z]/.test(v)&&/[0-9]/.test(v))score++;
      if(/[^a-zA-Z0-9]/.test(v))score++;
      if(score===3&&v.length>=12)score++;
      demo.dataset.level=String(score);
      hint.textContent=hints[score];
    });
  })();

  /* ---- 标签输入 ---- */
  (function(){
    const input=document.getElementById('tagInput');
    if(!input) return;
    const box=document.getElementById('tagBox');
    function addTag(raw){
      const v=raw.trim().replace(/,+$/,'');
      if(!v) return;
      if([...box.querySelectorAll('.tagchip > span')].some(s=>s.textContent===v)){ toast('标签已存在'); return; }
      const chip=document.createElement('span'); chip.className='tagchip';
      const label=document.createElement('span'); label.textContent=v;
      const x=document.createElement('button'); x.type='button'; x.className='tagx'; x.textContent='×'; x.setAttribute('aria-label','删除标签：'+v);
      x.addEventListener('click',()=>chip.remove());
      chip.append(label,x);
      box.insertBefore(chip,input);
      input.value='';
    }
    box.querySelectorAll('.tagx').forEach(x=>x.addEventListener('click',e=>e.target.closest('.tagchip').remove()));
    input.addEventListener('keydown',e=>{
      if(e.key==='Enter'||e.key===','){ e.preventDefault(); addTag(input.value); }
      else if(e.key==='Backspace'&&!input.value){
        const chips=box.querySelectorAll('.tagchip');
        if(chips.length) chips[chips.length-1].remove();
      }
    });
    input.addEventListener('blur',()=>addTag(input.value));
  })();

  /* ---- 验证码输入 ---- */
  (function(){
    const row=document.getElementById('otpRow');
    if(!row) return;
    const inputs=[...row.querySelectorAll('input')], hint=row.parentNode.querySelector('.otp-hint');
    function done(){ if(inputs.every(i=>i.value)){ toast('验证码已填完（演示，未提交）'); hint.textContent='已填完，可提交。'; } }
    inputs.forEach((cell,i)=>{
      cell.addEventListener('input',()=>{
        cell.value=cell.value.replace(/\D/g,'').slice(-1);
        if(cell.value&&i<inputs.length-1) inputs[i+1].focus();
        done();
      });
      cell.addEventListener('keydown',e=>{
        if(e.key==='Backspace'&&!cell.value&&i>0){ inputs[i-1].focus(); inputs[i-1].value=''; hint.textContent='输入自动前进；支持整段粘贴。'; e.preventDefault(); }
        if(e.key==='ArrowLeft'&&i>0){ inputs[i-1].focus(); e.preventDefault(); }
        if(e.key==='ArrowRight'&&i<inputs.length-1){ inputs[i+1].focus(); e.preventDefault(); }
      });
      cell.addEventListener('paste',e=>{
        const text=(e.clipboardData||window.clipboardData).getData('text').replace(/\D/g,'');
        if(text.length<2) return;
        e.preventDefault();
        inputs.forEach((c,j)=>{ c.value=text[j]||''; });
        inputs[Math.min(text.length,inputs.length-1)].focus();
        done();
      });
    });
  })();

  /* ---- 原地编辑 ---- */
  (function(){
    const text=document.getElementById('ieText');
    if(!text) return;
    let editing=false;
    function start(){
      if(editing) return;
      editing=true;
      const original=text.textContent;
      const input=document.createElement('input');
      input.className='ie-input'; input.type='text'; input.value=original;
      input.setAttribute('aria-label','编辑文字');
      text.replaceWith(input); input.focus(); input.select();
      function save(){ editing=false; text.textContent=input.value.trim()||original; input.replaceWith(text); }
      function cancel(){ editing=false; input.replaceWith(text); }
      input.addEventListener('keydown',e=>{
        if(e.key==='Enter'){ e.preventDefault(); save(); }
        else if(e.key==='Escape'){ e.preventDefault(); cancel(); }
      });
      input.addEventListener('blur',save);
    }
    text.addEventListener('click',start);
    text.addEventListener('keydown',e=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); start(); } });
  })();

  /* ---- 长按确认 ---- */
  (function(){
    const btn=document.getElementById('holdBtn');
    if(!btn) return;
    const fill=btn.querySelector('.holdfill'), label=btn.querySelector('.holdlabel');
    const originalLabel=label.textContent, DURATION=900;
    let timer=null, startAt=0;
    function tick(){
      const p=Math.min(1,(performance.now()-startAt)/DURATION);
      fill.style.width=(p*100)+'%';
      if(p>=1){ stop(); complete(); }
    }
    function start(){
      if(timer) return;
      btn.classList.remove('completed');
      startAt=performance.now();
      timer=setInterval(tick,40);
    }
    function stop(){
      clearInterval(timer); timer=null;
      fill.style.width='0%';
    }
    function complete(){
      btn.classList.add('completed');
      label.textContent='已删除（演示）';
      toast('草稿已删除（演示）');
      setTimeout(()=>{ btn.classList.remove('completed'); label.textContent=originalLabel; },1400);
    }
    function cancel(){
      if(!timer) return;
      stop();
      label.textContent='已取消，请按住不放';
      setTimeout(()=>{ label.textContent=originalLabel; },1200);
    }
    btn.addEventListener('pointerdown',e=>{ if(e.button===0||e.pointerType!=='mouse') start(); });
    btn.addEventListener('pointerup',cancel);
    btn.addEventListener('pointerleave',cancel);
    btn.addEventListener('pointercancel',cancel);
    btn.addEventListener('contextmenu',e=>e.preventDefault());
    btn.addEventListener('keydown',e=>{ if((e.key==='Enter'||e.key===' ')&&!e.repeat){ e.preventDefault(); start(); } });
    btn.addEventListener('keyup',e=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); cancel(); } });
  })();

  /* ---- 分裂按钮 ---- */
  (function(){
    const caret=document.getElementById('splitCaret');
    if(!caret) return;
    const menu=document.getElementById('splitMenu');
    function close(){ menu.hidden=true; caret.setAttribute('aria-expanded','false'); }
    caret.addEventListener('click',()=>{
      menu.hidden=!menu.hidden;
      caret.setAttribute('aria-expanded',String(!menu.hidden));
      if(!menu.hidden) menu.querySelector('button').focus();
    });
    menu.querySelectorAll('.split-pick').forEach(b=>b.addEventListener('click',()=>{ toast(b.textContent+'（演示）'); close(); caret.focus(); }));
    document.addEventListener('click',e=>{ if(!e.target.closest('.splitbtn-demo')) close(); });
    menu.addEventListener('keydown',e=>{ if(e.key==='Escape'){ close(); caret.focus(); } });
  })();

  /* ---- 悬浮按钮 ---- */
  (function(){
    const fab=document.getElementById('fabBtn');
    if(!fab) return;
    const actions=document.getElementById('fabActions');
    fab.addEventListener('click',()=>{
      const open=actions.hidden;
      actions.hidden=!open;
      fab.classList.toggle('open',open);
      fab.setAttribute('aria-expanded',String(open));
      fab.setAttribute('aria-label',open?'关闭快捷操作':'打开快捷操作');
    });
    document.addEventListener('keydown',e=>{
      if(e.key==='Escape'&&actions.hidden===false){ actions.hidden=true; fab.classList.remove('open'); fab.setAttribute('aria-expanded','false'); fab.focus(); }
    });
  })();

  /* ---- 大型菜单 ---- */
  (function(){
    const trigger=document.getElementById('megaTrigger');
    if(!trigger) return;
    const panel=document.getElementById('megaPanel');
    let closeTimer=null;
    function open(){ clearTimeout(closeTimer); panel.hidden=false; trigger.setAttribute('aria-expanded','true'); }
    function close(){ panel.hidden=true; trigger.setAttribute('aria-expanded','false'); }
    trigger.addEventListener('click',()=>{ panel.hidden?open():close(); });
    trigger.addEventListener('keydown',e=>{
      if(e.key==='ArrowDown'||e.key==='Enter'||e.key===' '){ e.preventDefault(); open(); panel.querySelector('button').focus(); }
      if(e.key==='Escape') close();
    });
    panel.addEventListener('keydown',e=>{
      if(e.key==='Escape'){ close(); trigger.focus(); }
    });
    document.addEventListener('click',e=>{ if(!e.target.closest('.mega-demo')) close(); });
  })();

  /* ---- 右键菜单 ---- */
  (function(){
    const zone=document.getElementById('ctxZone');
    if(!zone) return;
    const menu=document.createElement('div');
    menu.className='ctxmenu'; menu.hidden=true; menu.setAttribute('role','menu'); menu.setAttribute('aria-label','对象操作');
    [['重命名',false],['复制',false],['删除',true]].forEach(([name,danger])=>{
      const b=document.createElement('button');
      b.type='button'; b.setAttribute('role','menuitem'); b.textContent=name;
      if(danger) b.className='danger';
      b.addEventListener('click',()=>{ toast(name+'（演示）'); hide(); });
      menu.appendChild(b);
    });
    zone.appendChild(menu);
    function show(x,y){
      menu.hidden=false;
      const zw=zone.clientWidth, zh=zone.clientHeight, mw=menu.offsetWidth, mh=menu.offsetHeight;
      menu.style.left=Math.max(4,Math.min(x,zw-mw-4))+'px';
      menu.style.top=Math.max(4,Math.min(y,zh-mh-4))+'px';
      menu.querySelector('button').focus();
    }
    function hide(){ menu.hidden=true; }
    let pressTimer=null;
    zone.addEventListener('contextmenu',e=>{
      e.preventDefault();
      const rect=zone.getBoundingClientRect();
      show(e.clientX-rect.left,e.clientY-rect.top);
    });
    zone.addEventListener('pointerdown',e=>{
      if(e.pointerType==='mouse') return;
      const rect=zone.getBoundingClientRect();
      pressTimer=setTimeout(()=>show(e.clientX-rect.left,e.clientY-rect.top),550);
    });
    ['pointerup','pointermove','pointercancel'].forEach(t=>zone.addEventListener(t,()=>{ clearTimeout(pressTimer); }));
    zone.addEventListener('keydown',e=>{
      if(e.key==='Enter'||e.key===' '){ e.preventDefault(); show(zone.clientWidth/2-60,zone.clientHeight/2-40); }
    });
    menu.addEventListener('keydown',e=>{
      const items=[...menu.querySelectorAll('button')], i=items.indexOf(document.activeElement);
      if(e.key==='Escape'){ hide(); zone.focus(); }
      if(e.key==='ArrowDown'){ e.preventDefault(); items[(i+1)%items.length].focus(); }
      if(e.key==='ArrowUp'){ e.preventDefault(); items[(i-1+items.length)%items.length].focus(); }
    });
    document.addEventListener('click',e=>{ if(!e.target.closest('.ctxzone')) hide(); });
  })();

  /* ---- 视图切换 ---- */
  (function(){
    const body=document.getElementById('viewBody');
    if(!body) return;
    const buttons=[...document.querySelectorAll('.segb')];
    buttons.forEach(b=>b.addEventListener('click',()=>{
      buttons.forEach(x=>{ const on=x===b; x.classList.toggle('on',on); x.setAttribute('aria-pressed',String(on)); });
      body.dataset.view=b.dataset.view;
    }));
  })();

  /* ---- 表格列宽拖拽与列显隐 ---- */
  (function(){
    const tbl=document.getElementById('colTbl');
    if(!tbl) return;
    const ths=[...tbl.tHead.rows[0].cells];
    ths.forEach((th,i)=>{
      const grip=th.querySelector('.colgrip');
      if(!grip) return;
      grip.addEventListener('pointerdown',e=>{
        e.preventDefault();
        e.isTrusted&&grip.setPointerCapture(e.pointerId);
        grip.classList.add('on');
        const startX=e.clientX, startW=th.offsetWidth;
        function move(ev){
          const w=Math.max(56,startW+(ev.clientX-startX));
          th.style.width=w+'px';
        }
        function up(){ grip.classList.remove('on'); grip.removeEventListener('pointermove',move); grip.removeEventListener('pointerup',up); grip.removeEventListener('pointercancel',up); }
        grip.addEventListener('pointermove',move);
        grip.addEventListener('pointerup',up);
        grip.addEventListener('pointercancel',up);
      });
    });
    document.querySelectorAll('.colmenu input[data-col]').forEach(cb=>{
      cb.addEventListener('change',()=>{
        const idx=Number(cb.dataset.col), visible=cb.checked;
        [...tbl.rows].forEach(row=>{ row.cells[idx].style.display=visible?'':'none'; });
      });
    });
  })();

  /* ---- 拖动列排序 ---- */
  (function(){
    const tbl=document.getElementById('reTbl');
    if(!tbl) return;
    let drag=null;
    function moveCol(from,to){
      const rows=[...tbl.rows];
      if(to<0||to>=rows[0].cells.length||from===to) return;
      rows.forEach(row=>{
        const cells=row.cells, c=cells[from], ref=cells[to];
        if(to>from) row.insertBefore(c,ref.nextElementSibling);
        else row.insertBefore(c,ref);
      });
    }
    [...tbl.tHead.rows[0].cells].forEach((th,i)=>{
      th.addEventListener('pointerdown',e=>{
        if(e.button!==0) return;
        drag={th,i,startX:e.clientX,dx:0};
        e.isTrusted&&th.setPointerCapture(e.pointerId);
        th.classList.add('col-dragging');
        e.preventDefault();
      });
    });
    tbl.addEventListener('pointermove',e=>{
      if(!drag) return;
      drag.dx=e.clientX-drag.startX;
      drag.th.style.transform=`translateX(${drag.dx}px)`;
      const w=drag.th.offsetWidth;
      if(drag.dx>w/2){ moveCol(drag.i,drag.i+1); drag.i+=1; drag.startX+=w; drag.th.style.transform=''; }
      else if(drag.dx<-w/2){ moveCol(drag.i,drag.i-1); drag.i-=1; drag.startX-=w; drag.th.style.transform=''; }
    });
    function endDrag(){
      if(!drag) return;
      drag.th.style.transform='';
      drag.th.classList.remove('col-dragging');
      toast('列顺序已调整（演示）');
      drag=null;
    }
    tbl.addEventListener('pointerup',endDrag);
    tbl.addEventListener('pointercancel',endDrag);
  })();

  /* ---- 单元格编辑 ---- */
  (function(){
    document.querySelectorAll('.edittarget').forEach(cell=>{
      let editing=false;
      function start(){
        if(editing) return;
        editing=true;
        const original=cell.textContent;
        const input=document.createElement('input');
        input.className='cell-input'; input.type='text'; input.value=original;
        input.setAttribute('aria-label','编辑单元格');
        cell.textContent=''; cell.appendChild(input);
        input.focus(); input.select();
        function save(){
          editing=false;
          const v=input.value.trim();
          cell.textContent=v||original;
          cell.setAttribute('aria-label','双击或回车编辑：'+(v||original));
          if(!v) toast('内容不能为空，已恢复原值');
        }
        function cancel(){ editing=false; cell.textContent=original; }
        input.addEventListener('keydown',e=>{
          if(e.key==='Enter'){ e.preventDefault(); input.blur(); }
          else if(e.key==='Escape'){ e.preventDefault(); input.removeEventListener('blur',save); cancel(); cell.focus(); }
        });
        input.addEventListener('blur',save);
      }
      cell.addEventListener('dblclick',start);
      cell.addEventListener('keydown',e=>{ if(e.target===cell&&e.key==='Enter'){ e.preventDefault(); start(); } });
    });
  })();

  /* ---- 复选框：父级全选与半选 ---- */
  (function(){
    const all=document.getElementById('ckAll');
    if(!all) return;
    const kids=[...document.querySelectorAll('.ck-child')];
    function sync(){
      const n=kids.filter(k=>k.checked).length;
      all.checked=n===kids.length;
      all.indeterminate=n>0&&n<kids.length;
    }
    all.addEventListener('change',()=>{ kids.forEach(k=>k.checked=all.checked); sync(); });
    kids.forEach(k=>k.addEventListener('change',sync));
    sync();
  })();

  /* ---- 按钮：复制成功反馈 ---- */
  (function(){
    const btn=document.getElementById('copyDemoBtn');
    if(!btn) return;
    const original=btn.textContent;
    btn.addEventListener('click',()=>{
      btn.textContent='✓ 已复制';btn.classList.add('ds-success');
      btn.disabled=true;
      setTimeout(()=>{ btn.textContent=original; btn.disabled=false;btn.classList.remove('ds-success'); },1600);
    });
  })();

  /* ---- 文本域：字数统计 ---- */
  (function(){
    const ta=document.getElementById('taCount');
    if(!ta) return;
    const num=document.getElementById('taCountNum'), MAX=80;
    ta.addEventListener('input',()=>{
      if(ta.value.length>MAX){ ta.value=ta.value.slice(0,MAX); toast('最多 80 字'); }
      num.textContent=ta.value.length+' / '+MAX;
      num.style.color=(MAX-ta.value.length)<=10?'#e11d48':'';
    });
  })();


  /* ---- 无限滚动 ---- */
  (function(){
    const list=document.getElementById('infList');
    if(!list) return;
    const status=document.getElementById('infStatus');
    let page=0,loading=false,done=false;
    list.addEventListener('scroll',()=>{
      if(loading||done) return;
      if(list.scrollTop+list.clientHeight<list.scrollHeight-24) return;
      loading=true;status.textContent='正在加载…';
      setTimeout(()=>{
        page++;
        for(let i=1;i<=3;i++){
          const d=document.createElement('div');d.className='inf-item';
          d.textContent='信息条目 '+(page*3+i);
          list.insertBefore(d,status);
        }
        loading=false;
        if(page>=2){done=true;status.textContent='已经到底了';}
        else status.textContent='下滑自动加载…';
      },450);
    });
  })();

  /* ---- 加载更多 ---- */
  (function(){
    const btn=document.getElementById('lmBtn');
    if(!btn) return;
    const list=document.getElementById('lmList');
    let round=0;
    btn.addEventListener('click',()=>{
      if(btn.disabled) return;
      btn.disabled=true;btn.textContent='正在加载…';
      setTimeout(()=>{
        round++;
        ['条目 C'+round,'条目 D'+round,'条目 E'+round].forEach(t=>{
          const d=document.createElement('div');d.className='inf-item';d.textContent=t;list.appendChild(d);
        });
        if(round>=2){btn.textContent='没有更多了';btn.disabled=true;}
        else{btn.disabled=false;btn.textContent='加载更多';}
      },500);
    });
  })();

  /* ---- 返回顶部 ---- */
  (function(){
    const page=document.getElementById('bttPage');
    if(!page) return;
    const btn=document.getElementById('bttBtn');
    page.addEventListener('scroll',()=>{btn.hidden=page.scrollTop<60;});
    btn.addEventListener('click',()=>{page.scrollTo({top:0,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});});
  })();

  /* ---- 条件步骤 ---- */
  (function(){
    const radios=document.querySelectorAll('input[name="acct"]');
    if(!radios.length) return;
    const extra=document.querySelector('#condSteps li[data-extra]');
    const note=document.getElementById('condNote');
    radios.forEach(r=>r.addEventListener('change',()=>{
      const company=document.querySelector('input[name="acct"]:checked').value==='company';
      extra.hidden=!company;
      note.hidden=!company;
    }));
  })();

  /* ---- 高级设置 ---- */
  (function(){
    const t=document.getElementById('advToggle');
    if(!t) return;
    const body=document.getElementById('advBody');
    t.addEventListener('click',()=>{
      body.hidden=!body.hidden;
      t.setAttribute('aria-expanded',String(!body.hidden));
      t.textContent=body.hidden?'高级设置 ▸':'高级设置 ▴';
    });
  })();

  /* ---- 上下文选项 ---- */
  (function(){
    const ck=document.getElementById('ctxoCheck');
    if(!ck) return;
    const body=document.getElementById('ctxoBody');
    ck.addEventListener('change',()=>{body.hidden=!ck.checked;});
  })();


  /* ---- 自动保存 ---- */
  (function(){
    const ta=document.getElementById('asInput');
    if(!ta) return;
    const st=document.getElementById('asStatus');
    let timer=null;
    ta.addEventListener('input',()=>{
      st.textContent='正在编辑…';st.className='as-status';
      clearTimeout(timer);
      timer=setTimeout(()=>{
        if(!ta.value.trim()){st.textContent='未保存';st.className='as-status';return;}
        st.textContent='保存中…';st.className='as-status saving';
        setTimeout(()=>{st.textContent='已保存 ✓';st.className='as-status saved';},400);
      },700);
    });
  })();

  /* ---- 虚拟列表 ---- */
  (function(){
    const list=document.getElementById('vlList');
    if(!list) return;
    const stat=document.getElementById('vlStat');
    const TOTAL=1000,ROW=26;
    list.style.height='136px';
    const spacer=document.createElement('div');
    spacer.style.height=TOTAL*ROW+'px';
    list.appendChild(spacer);
    function render(){
      const first=Math.max(0,Math.floor(list.scrollTop/ROW)-3);
      const visible=Math.ceil(list.clientHeight/ROW)+6;
      list.querySelectorAll('.vl-row').forEach(r=>r.remove());
      for(let i=first;i<Math.min(TOTAL,first+visible);i++){
        const row=document.createElement('div');row.className='vl-row';
        row.style.top=i*ROW+'px';
        row.innerHTML='<span>日志行 '+(i+1)+'</span><span>info</span>';
        list.appendChild(row);
      }
      stat.textContent='共 '+TOTAL+' 行 · 当前渲染 '+visible+' 行';
    }
    list.addEventListener('scroll',render,{passive:true});
    render();
  })();

  /* ---- 整卡可点击 ---- */
  (function(){
    const card=document.querySelector('.clk-card');
    if(!card) return;
    card.addEventListener('keydown',e=>{
      if(e.key!=='Enter') return;
      if(e.target.closest('.clk-share')){toast('仅分享，未打开详情（演示）');return;}
      toast('打开详情（演示）');
    });
  })();



/* 演示交互统一委托：data-cmd 替代内联 on*=，便于 CSP 与维护。 */
(function(){
  function onCmd(e){
    var el = e.target.closest('[data-cmd]');
    if(!el) return;
    var arg = el.dataset.arg;
    switch(el.dataset.cmd){
      case 'openDrawer': openDrawer(); break;
      case 'closeDrawer': closeDrawer(); break;
      case 'openModal': openModal(); break;
      case 'closeModal': closeModal(); if(arg) toast(arg); break;
      case 'openCmdk': openCmdk(); break;
      case 'closeCmdkSelf': if(e.target===el) closeCmdk(); break;
      case 'demoSearch': demoSearch(el); break;
      case 'demoRegister': demoRegister(); break;
      case 'pickDD': pickDD(el); break;
      case 'toggleDD': toggleDD(e); break;
      case 'toggleAcc': toggleAcc(el); break;
      case 'toggleInfoPopover': toggleInfoPopover(e); break;
      case 'setStep': setStep(+arg); break;
      case 'stepNum': stepNum(+arg); break;
      case 'switchTab': switchTab(el, +arg); break;
      case 'removeParent': el.parentNode.remove(); break;
      case 'prevent': e.preventDefault(); break;
      case 'toast': toast(arg); break;
      case 'toastChecked': toast(el.checked ? el.dataset.on : el.dataset.off); break;
    }
  }
  document.addEventListener('click', onCmd);
  document.addEventListener('keydown', function(e){
    if(e.key==='Enter' && e.target.matches('[data-cmd="searchEnter"]')){ e.preventDefault(); demoSearch(e.target); }
  });
  document.addEventListener('input', function(e){
    if(e.target.matches('[data-cmd="rangeLabel"]')) e.target.nextElementSibling.textContent = e.target.value + '%';
  });
  document.addEventListener('submit', function(e){
    if(e.target.matches('.demo-form')) e.preventDefault();
  });
})();

document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeCmdk();if(document.getElementById('modal'))closeModal();if(document.getElementById('dmask'))closeDrawer();closePopover();}});

const skeletonCard=document.querySelector('.ds-skeleton-card');
if(skeletonCard){
  const image=skeletonCard.querySelector('img');
  function revealSkeleton(){
    skeletonCard.classList.add('is-loaded');
    skeletonCard.setAttribute('aria-busy','false');
    skeletonCard.querySelector('.ds-skeleton-content').setAttribute('aria-hidden','false');
    skeletonCard.querySelector('[role=status]').textContent='场景加载完成';
  }
  function finishSkeleton(){
    if(image.complete&&image.naturalWidth)revealSkeleton();
    else image.addEventListener('load',revealSkeleton,{once:true});
  }
  if(matchMedia('(prefers-reduced-motion: reduce)').matches)finishSkeleton();
  else setTimeout(finishSkeleton,1400);
}

});
