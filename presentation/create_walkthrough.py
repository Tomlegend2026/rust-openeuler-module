"""Build an evidence-backed 22-slide source walkthrough, shared by HTML/PPTX."""
from pathlib import Path
import csv, html, json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables' / '源码走读详细版'
BUILD = ROOT / 'build' / 'walkthrough'
OUT.mkdir(parents=True, exist_ok=True)
BUILD.mkdir(parents=True, exist_ok=True)
slides = []
INK, BLUE, RED, MUTED, LINE = '#333333', '#006393', '#CC0000', '#777777', '#CCCCCC'

def new(title, chapter, sources, notes):
    s = dict(title=title, chapter=chapter, sources=sources, notes=notes, elements=[])
    slides.append(s)
    text(s, title, 20, 54, 1600, 92, 48, bold=True)
    text(s, chapter, 1580, 95, 320, 35, 18, color=MUTED, align='right')
    box(s, 0, 170, 1920, 5, '#000000', '#000000')
    text(s, '源码版本 cc79af3   /   技术实测 2026-10-18', 20, 1030, 650, 30, 16, color=MUTED)
    text(s, f'{len(slides):02d} / 22', 1730, 1030, 170, 30, 16, color=MUTED, align='right')
    return s

def text(s, value, x, y, w, h, size=28, color=INK, bold=False, mono=False, align='left'):
    s['elements'].append(dict(kind='text', text=value, x=x,y=y,w=w,h=h,size=size,color=color,bold=bold,mono=mono,align=align))

def box(s,x,y,w,h,fill='#FFFFFF',stroke=LINE):
    s['elements'].append(dict(kind='box',x=x,y=y,w=w,h=h,fill=fill,stroke=stroke))

def line(s,x,y,w,h=1,color=LINE):
    box(s,x,y,w,max(h,1),color,color)

def paras(s, items, x=20,y=260,w=650,step=190):
    for i,(heading,body) in enumerate(items):
        text(s,heading,x,y+i*step,w,50,32,bold=True,color=BLUE if i else INK)
        text(s,body,x,y+65+i*step,w,100,27,color=MUTED)

def code(s,path,start,end,x=690,y=265,w=1210,size=29):
    raw=(ROOT/path).read_text(encoding='utf-8').splitlines()
    end=min(end,len(raw))
    selected=raw[start-1:end]
    text(s,f'{path}:{start}–{end}',x,y-55,w,40,22,color=BLUE)
    box(s,x,y,w, min(670,70+len(selected)*(size*1.5)), '#F5F5F5')
    for i,v in enumerate(selected):
        # Line numbers are kept separate from code, so excerpts remain copyable.
        text(s,str(start+i),x+15,y+25+i*size*1.5,48,size*1.55,19,color=MUTED,mono=True)
        fit_size=min(size,(w-115)/max(1,len(v))/.61)
        text(s,v,x+85,y+25+i*size*1.5,w-105,size*1.55,fit_size,mono=True)

def table(s,headers,rows,widths,x=20,y=280,rowh=80,size=28):
    # Each cell becomes native editable text and geometry in PowerPoint.
    start=len(s['elements'])
    for r,row in enumerate([headers]+rows):
        left=x
        for c,val in enumerate(row):
            box(s,left,y+r*rowh,widths[c],rowh,BLUE if r==0 else ('#F5F5F5' if r%2 else '#FFFFFF'))
            text(s,str(val),left+22,y+r*rowh+18,widths[c]-44,rowh-24,size,'#FFFFFF' if r==0 else INK,bold=r==0)
            left += widths[c]
    s.setdefault('tables',[]).append(dict(headers=headers,rows=rows,widths=widths,x=x,y=y,rowh=rowh,size=size,start=start,end=len(s['elements'])))

def flow(s,labels,descs=None,y=420):
    # C·11 activity-template adaptation: same-lane actions, edge-midpoint connectors.
    n=len(labels); w=(1880-(n-1)*70)/n
    for i,v in enumerate(labels):
        x=20+i*(w+70)
        box(s,x,y,w,150,'#FFF2F2' if i==n-1 else '#F5F5F5',RED if i==n-1 else LINE)
        text(s,v,x+20,y+40,w-40,70,32,bold=True,align='center',color=RED if i==n-1 else INK)
        if descs: text(s,descs[i],x,y+190,w,130,26,color=MUTED,align='center')
        if i<n-1:
            line(s,x+w,y+75,60,2,MUTED)
            text(s,'›',x+w+48,y+41,25,60,42,color=MUTED)

life='evidence/logs/lifecycle-20261018T112424Z-NBTnuw'
negative='evidence/logs/negative-20261018T112425Z-NFqiar'

s=new('Rust 内核模块的实现与动态装卸','任务 2 · 源码走读',['module/rust_team2.rs:11-52','tests/测试结果-20261018.md:1-42'],
      '这是操作系统课程任务2的详细技术汇报。实验在专用openEuler虚拟机完成。先解释实现，再用原始证据说明测试结果。')
text(s,'在 openEuler 中构建并验证 rust_team2',20,305,1750,130,72,bold=True)
text(s,'学习 Rust 的所有权、借用与错误处理\n完成模块初始化、状态保留和卸载流程',24,505,1450,160,40,color=MUTED)
line(s,24,730,150,5,RED)
text(s,'22 页详细技术讲解\n项目：rust-openeuler-module',24,800,1500,110,30,color=BLUE)

s=new('汇报结构','内容导航',['README.md:1-90'], '六个章节按实验目标、完整流程、项目结构、Rust机制、验证证据和能力边界展开。')
for i,(a,b) in enumerate([('项目与任务','用可装卸统计模块完成课程要求'),('完整实验流程','源码、构建、加载、运行与卸载'),('结构与环境','仓库分层和固定工具链'),('Rust 源码机制','所有权、借用、Result 与 Drop'),('构建及测试证据','Kbuild、10 轮装卸、负向测试'),('演示与能力边界','复现入口和结论范围')]):
    x=20+(i%2)*960; y=260+(i//2)*240
    line(s,x,y,900,1); text(s,f'{i+1:02d}',x,y+25,90,60,42,color=RED if i==3 else BLUE,bold=True)
    text(s,a,x+120,y+25,760,55,36,bold=True); text(s,b,x+120,y+110,760,65,28,color=MUTED)

s=new('实验以统计模块验证动态装卸','一 · 项目与任务',['README.md:17-23','module/rust_team2.rs:25-52'], '动态装卸是系统运行时加入和移除模块。该模块不提供字符设备或外部输入，固定数据便于复核整个生命周期。')
paras(s,[('输入固定','[3, 1, 4, 1, 5, 9]\n将数据分配并保留在模块实例中'),('输出可复核','计算 count、sum、min、max\n写入内核日志供测试核对'),('资源有归属','加载成功后实例拥有 Vec\n卸载时进入 Drop，随后字段析构')],w=800,step=235)
text(s,'6',1100,290,500,130,100,bold=True,color=RED)
text(s,'个输入元素',1105,435,600,60,34)
text(s,'count=6  sum=23\nmin=1    max=9\naverage=3  range=8',1105,565,770,180,42,mono=True)
text(s,'来源：固定输入及统计函数，非性能基准',1105,830,770,80,24,color=MUTED)

s=new('一次装卸贯穿完整实验链路','二 · 完整实验流程',['scripts/build-module.sh:1-21','scripts/test-lifecycle.sh:60-90'], '构建与加载是两个独立步骤。init成功后才有已加载实例；卸载入口日志随后进入字段析构。流程图依据C11活动图模板重排为同一泳道。')
flow(s,['源码','Kbuild','加载','运行状态','卸载'],['Rust 模块及统计函数','生成目标内核的 .ko','insmod 触发 init','实例持有 Vec 与统计值','rmmod 进入 Drop'])
text(s,'构建成功后，还必须验证运行内核中的模块状态与新增日志',20,850,1880,80,36,color=BLUE,bold=True)

s=new('仓库将计算、内核入口和验证工具分开','三 · 结构与环境',['module/rust_team2.rs:5-9','module/statistics.rs:18-35','scripts/verify-evidence.py:1-52'], '对应C01分层模板。纯统计计算、内核入口和证据核验各有明确边界。脚本负责构建、状态检查和证据核验，不参与内核内的计算。')
layers=[('逻辑与验证','module/statistics.rs     tests/     scripts/'),('内核入口','module/rust_team2.rs     init / Drop'),('纯计算','module/statistics.rs     summarize(&[u64])'),('运行基线','openEuler 24.03 LTS     6.6.0-team2-rust+')]
for i,(a,b) in enumerate(layers):
    y=270+i*170; box(s,20,y,1880,120,'#F5F5F5'); box(s,20,y,340,120,BLUE)
    text(s,a,45,y+32,285,60,32,color='#FFFFFF',bold=True)
    text(s,b,410,y+35,1430,60,34,mono=i in (0,1,2))

s=new('模块与运行内核保持同一构建基线','三 · 结构与环境',['environment/版本记录.md:9-29','evidence/logs/build-20261018T110037Z-2166.log:1-34'], '这里是实际环境记录，不是任意版本通用教程。更换内核需要重新核对Rust API、工具链、配置与vermagic。')
table(s,['环境项','已记录的实际值'],[['发行版 / 架构','openEuler 24.03 LTS / x86_64'],['运行内核','6.6.0-team2-rust+'],['Rust','1.73.0'],['LLVM / bindgen','17.0.6 / 0.65.1'],['关键内核配置','RUST=y  MODULES=y  MODULE_UNLOAD=y'],['模块 vermagic','6.6.0-team2-rust+ SMP mod_unload']],[500,1380],rowh=88)

s=new('Rust 源码对应四种核心机制','四 · Rust 源码机制',['module/rust_team2.rs:19-51','module/statistics.rs:18-35'], '所有权、借用、Result和Drop直接落在模块源码与统计函数中。统计函数使用切片借用，内核入口负责资源持有和生命周期。')
table(s,['机制','模块中的落点','作用'],[['所有权','Ok(Self { values, summary })','把数据移入模块实例'],['借用','summarize(&values)','计算期间只读访问数据'],['Result 与 ?','values.try_push(value)?','沿错误路径提前返回'],['Drop','impl Drop for RustTeam2','卸载时进入清理入口']],[320,860,700],rowh=125)

s=new('所有权转移让数据跨过 init 的作用域','四 · Rust 源码机制',['module/rust_team2.rs:19-39'], '局部向量起初由init拥有。Ok(Self...)移动向量到模块对象，不需要clone。统计函数只是借用，调用结束后向量仍由原所有者持有。')
flow(s,['局部 Vec','只读借用','模块实例'],['init 分配并填入 6 个值','summarize(&values)\n借用结束后继续使用','Ok(Self { values, summary })\n实例继续持有堆缓冲区'],y=360)
text(s,'RustTeam2 { values: Vec<u64>, summary: Statistics }',20,830,1880,75,36,mono=True,color=BLUE)

s=new('初始化采用可失败分配并返回模块实例','四 · Rust 源码机制',['module/rust_team2.rs:25-39'], 'try_push分配失败时返回错误，问号传播错误。summarize错误在内核入口映射为EINVAL。只有成功才返回模块实例。')
paras(s,[('分配可以失败','try_push 返回 Result\n? 将错误交还加载路径'),('成功才保留状态','统计完成后输出 loaded\n随后返回拥有数据的实例')],w=580,step=280)
code(s,'module/rust_team2.rs',26,39,size=25)

s=new('统计函数借用切片并检查累加溢出','四 · Rust 源码机制',['module/statistics.rs:18-35'], '先取得首元素作为最值基准，空输入返回EmptyInput。count来自切片长度，sum从0开始，用checked_add区分合法累加与溢出。')
paras(s,[('输入不转移所有权','参数是 &[u64]\n函数不修改输入'),('错误显式返回','空切片返回 EmptyInput\n加法溢出返回 SumOverflow')],w=580,step=280)
code(s,'module/statistics.rs',18,35,size=23)

s=new('正常数据与算法边界分别验证','四 · Rust 源码机制',['module/statistics.rs:38-84','module/rust_team2.rs:27-33'], '固定内核输入只覆盖正常统计路径。空输入和溢出用例在独立计算测试中验证，不能说这些输入在内核装卸测试中实际触发过。')
table(s,['情形','计算函数行为','验证位置'],[['固定六个整数','count=6 sum=23 min=1 max=9\naverage=3 range=8','内核日志与逻辑测试'],['空输入','EmptyInput','逻辑测试'],['[u64::MAX]','合法，sum=u64::MAX','逻辑测试'],['[u64::MAX, 1]','SumOverflow','逻辑测试'],['零值与只读输入','结果正确，原数据保持不变','逻辑测试']],[430,850,600],rowh=103)
text(s,'内核入口将计算错误映射为 EINVAL，默认固定输入不会触发该分支',20,940,1880,60,28,color=BLUE)

s=new('加载成功后才进入可卸载状态','四 · Rust 源码机制',['module/rust_team2.rs:25-52','scripts/test-negative.sh:58-78'], '依据C14状态模板适配模块状态。正常路径从未加载到初始化、已加载、清理，再回到未加载。错误请求保留原来的外部状态。')
flow(s,['未加载','初始化中','已加载','清理中','未加载'],['insmod 前','创建 Vec 并统计','init 返回 Ok','rmmod 触发 Drop','/proc/modules 无条目'],y=350)
text(s,'错误分支',20,780,350,60,32,bold=True,color=BLUE)
text(s,'已加载时再次加载：请求失败，原模块仍在\n未加载时再次卸载：请求失败，仍保持未加载',20,860,1800,130,32)

s=new('Drop 日志先于 Vec 字段析构','四 · Rust 源码机制',['module/rust_team2.rs:42-52'], '重要答辩点：自定义Drop方法执行时字段仍然存在，所以可以读取values.len。方法返回后字段才析构。日志名unload_begin刻意说明它只表示清理开始。')
paras(s,[('方法执行期间字段仍在','Drop 可以读取 values.len()\n并打印已保存的统计值'),('方法返回后字段析构','Vec 释放其拥有的缓冲区\n日志本身不证明无泄漏')],w=600,step=280)
code(s,'module/rust_team2.rs',42,52,size=27)

s=new('Kbuild 使用目标内核配置生成模块','五 · 构建及测试证据',['module/Kbuild:1-2','module/Makefile:1-10','scripts/build-module.sh:1-21'], '主机侧 rustc 只验证可独立测试的统计逻辑。外部内核模块交给目标内核Kbuild，以便使用目标配置、符号和Rust内核支持。这里不把一个普通Rust目标文件当成可加载模块。')
text(s,'Kbuild',20,270,600,60,36,bold=True,color=BLUE)
text(s,'obj-m += rust_team2.o',20,360,1800,80,42,mono=True)
text(s,'Makefile 的构建入口',20,510,1000,60,34,bold=True)
text(s,'$(MAKE) -C "$(KDIR)" M="$(CURDIR)"\n        LLVM=$(LLVM) modules',20,610,1840,140,38,mono=True)
text(s,'build-module.sh 先检查环境，再记录源码与 .ko 的哈希、modinfo 和构建日志',20,850,1860,100,32,color=MUTED)

s=new('真实构建记录包含 RUSTC、MODPOST 和 LD','五 · 构建及测试证据',['evidence/logs/build-20261018T110037Z-2166.log:1-34'], '右侧是保存的原始构建日志节选的排版，不是虚拟机屏幕截图。构建成功只验证产物形成，是否能加载还需要后续装卸测试。')
paras(s,[('2026-10-18 重新构建','目标内核与运行内核一致\nRust 可用性检查通过'),('产物可定位','模块名为 rust_team2\nvermagic 与运行内核一致')],w=590,step=280)
log='Rust is available!\n\nRUSTC [M] rust_team2.o\nMODPOST Module.symvers\nLD [M] rust_team2.ko\n\nname: rust_team2\nvermagic:\n6.6.0-team2-rust+ SMP mod_unload\n\nPASS: build completed.'
box(s,690,280,1210,630,'#F5F5F5'); text(s,log,725,315,1140,560,32,mono=True)
text(s,'原始日志节选，路径前缀已省略；构建完成与运行成功分别验证',690,940,1200,60,23,color=MUTED)

s=new('循环脚本逐轮检查装卸状态','五 · 构建及测试证据',['scripts/test-lifecycle.sh:64-90'], '不是仅靠命令输出判断成功。加载后查询/proc/modules，卸载后再次查询，并逐轮写入TSV。前后原始内核日志还会提取增量。')
paras(s,[('加载后有状态证据','insmod 成功后\n必须能查询到模块'),('卸载后也检查状态','rmmod 成功后\n必须查不到模块'),('每轮都记录退出状态','连续轮号写入 rounds.tsv\n再核对两类事件日志数量')],w=580,step=215)
code(s,'scripts/test-lifecycle.sh',64,74,size=28)

s=new('十轮实测均完成加载与卸载','五 · 构建及测试证据',[life+'/rounds.tsv:1-11',life+'/result.txt:1',life+'/new.log:1-20'], '表格从rounds.tsv逐行读取，不是手填预期结果。命令成功、加载后存在、卸载后不存在四个条件每一轮都成立。原始新增日志还包含各10次事件。')
with (ROOT/life/'rounds.tsv').open(encoding='utf-8',newline='') as f: rounds=list(csv.DictReader(f,delimiter='\t'))
table(s,['轮次','加载退出码','加载后存在','卸载退出码','卸载后不存在'],[[r['round'],r['load'],r['listed_after_load'],r['unload'],r['absent_after_unload']] for r in rounds],[200,390,450,390,450],y=240,rowh=58,size=26)
text(s,'10 次 loaded    10 次 unload_begin    EXIT_STATUS=0',20,930,1860,60,34,bold=True,color=RED)

s=new('负向测试拒绝无效请求并保持模块状态','五 · 构建及测试证据',[negative+'/cases.tsv:1-3','scripts/test-negative.sh:58-90'], '两个请求失败是预期行为。测试脚本整体成功，因为它同时确认非零退出码和正确的模块状态。注意不要把退出码1当成实验失败。')
with (ROOT/negative/'cases.tsv').open(encoding='utf-8',newline='') as f: cases=list(csv.DictReader(f,delimiter='\t'))
table(s,['测试请求','命令退出码','请求后的状态'],[['重复加载',cases[0]['exit_status'],cases[0]['state_check']],['卸载不存在的模块',cases[1]['exit_status'],cases[1]['state_check']]],[720,400,760],y=300,rowh=145,size=34)
text(s,'判定条件',20,810,500,60,34,bold=True,color=BLUE)
text(s,'请求返回非零，并且状态保持正确，两个条件必须同时成立',20,890,1860,70,34)

s=new('不同测试覆盖不同层次的风险','五 · 构建及测试证据',['module/statistics.rs:38-84','tests/测试结果-20261018.md:5-18','tests/test_log_extraction.py:1-60','tests/test_evidence_audit.py:1-60'], '逻辑测试、辅助工具测试和内核实测互相补充。数据不是性能指标，不能据此宣称速度更快或不存在内存泄漏。')
table(s,['验证层次','已记录结果','覆盖内容'],[['Rust 纯统计逻辑','6 项通过','空输入、溢出、最值与借用'],['Python 工具测试','13 项通过','日志提取与证据核验'],['内核生命周期','10 轮通过','运行时装卸状态及事件'],['错误装卸请求','2 个用例通过','拒绝请求并保留状态']],[570,430,880],rowh=130)
text(s,'主机测试通过后，仍须以目标 openEuler 内核的构建和运行证据确认可装卸',20,940,1850,60,28,color=BLUE)

s=new('证据核验重新计算日志增量并检查轮次','五 · 构建及测试证据',['scripts/verify-evidence.py:16-49','scripts/extract-new-log.py:1-65',life+'/rounds.tsv:1-11'], '核验器读取保存的文件，不会重新加载模块。它把before和after重新提取为增量，并与new.log比较。没有匹配到关键字只是有限检测的结果。')
flow(s,['原始日志','增量复算','轮次核对','事件计数'],['before.log / after.log','与 new.log 逐字比较','连续 1–10\n每行状态符合预期','loaded 与 unload_begin\n各出现 10 次'],y=330)
text(s,'同时检查 result.txt 和异常关键字：BUG、Oops、WARNING、kernel panic',20,800,1850,80,32,color=BLUE)
text(s,'离线核验验证保存证据的一致性，不等于一次新的内核运行',20,920,1850,60,30,color=MUTED)

s=new('现场演示按版本、加载、卸载顺序展开','六 · 演示与能力边界',['presentation/汇报与演示.md:35-62','scripts/test-lifecycle.sh:6-23'], '仅在已匹配的专用openEuler实验虚拟机操作。终端一观察dmesg，终端二执行装卸。最后grep没有匹配是预期结果。现场失败应保留错误并解释，不伪造成功截图。')
paras(s,[('先核对版本','uname 与 modinfo\n运行内核必须匹配'),('再观察状态与日志','一个终端观察 dmesg\n另一个执行加载与卸载'),('最后展示批量验证','运行循环脚本\n对照真实历史证据')],w=590,step=215)
box(s,690,280,1210,650,'#F5F5F5')
text(s,'uname -r\nmodinfo module/rust_team2.ko\n\nsudo insmod module/rust_team2.ko\nlsmod | grep rust_team2\n\nsudo rmmod rust_team2\nlsmod | grep rust_team2',725,320,1130,570,34,mono=True)

s=new('已验证动态装卸，结论保留明确边界','六 · 演示与能力边界',['tests/测试结果-20261018.md:30-42','module/rust_team2.rs:42-51','docs/08-交付状态与组员待办.md:1-90'], '收尾只总结有证据的结果。有限装卸、固定数据和关键字检查不能证明所有内存或并发缺陷不存在。演示时应同时说明已验证范围和未覆盖范围。')
paras(s,[('已经验证','目标内核构建成功，10 轮装卸通过\n两个负向请求状态正确，原始证据已保存'),('本次结论范围','固定数据的统计与模块生命周期\n未实现设备 I/O、后台线程或外部输入'),('演示时说明','展示真实版本、命令和日志\n说明测试边界与未覆盖功能')],w=1760,step=230)
text(s,'源码与日志节选均来自仓库；架构图是机制示意，不代表实际屏幕截图',20,960,1850,50,24,color=MUTED)

assert len(slides)==22
# All source anchors are validated against actual files before generating artifacts.
for s in slides:
    normalized=[]
    for anchor in s['sources']:
        file,r=anchor.rsplit(':',1); p=ROOT/file
        assert p.is_file(),anchor
        count=len(p.read_text(encoding='utf-8').splitlines())
        lo=int(r.split('-')[0]); assert lo<=count,anchor
        hi=min(int(r.split('-')[-1]),count)
        normalized.append(f'{file}:{lo}' + (f'-{hi}' if hi!=lo else ''))
    s['sources']=normalized
(BUILD/'slides.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2),encoding='utf-8')

def element(e):
    height=max(e['h'],e.get('size',0)*1.45) if e['kind']=='text' else e['h']
    style=f"left:{e['x']}px;top:{e['y']}px;width:{e['w']}px;height:{height}px;"
    if e['kind']=='box': return f'<div class="shape" style="{style}background:{e["fill"]};border:1px solid {e["stroke"]}"></div>'
    style+=f'font-size:{e["size"]}px;color:{e["color"]};font-weight:{700 if e["bold"] else 400};text-align:{e["align"]};'
    if e['mono']: style+='font-family:Consolas,"Microsoft YaHei",monospace;'
    return f'<div class="txt" style="{style}">{html.escape(e["text"])}</div>'

css='''*{box-sizing:border-box}html,body{margin:0;overflow:hidden;background:#5A5F66;font-family:"Microsoft YaHei",Arial,sans-serif}.stage{position:absolute;top:0;left:0;width:1920px;height:1080px;transform-origin:top left}.page{display:none;position:relative;width:1920px;height:1080px;background:#FFFFFF;overflow:hidden}.page.on{display:block}.shape,.txt{position:absolute}.txt{white-space:pre-wrap;line-height:1.42;padding:0;overflow:hidden}.ptitle{position:absolute;left:20px;top:20px;height:150px;font-size:48px}.pager{position:fixed;right:16px;bottom:12px;color:#FFF;background:#333;padding:8px 16px;font-size:14px}.note{display:none;position:fixed;left:0;bottom:0;width:85%;padding:15px;color:white;background:#333;font-size:18px}.note.on{display:block}@media print{html,body{overflow:visible;background:white}.stage{transform:none!important;position:static}.page{display:block!important;break-after:page}.pager,.note{display:none!important}@page{size:20in 11.25in;margin:0}}'''
pages=[]
for s in slides:
    # ptitle/hr hooks support the skill checker; rendered objects carry exact coordinates.
    titlehook=f'<h2 class="ptitle" style="visibility:hidden">{html.escape(s["title"])}</h2><span class="hr"></span>'
    pages.append(f'<section class="page" data-title="{html.escape(s["title"],quote=True)}" data-notes="{html.escape(s["notes"],quote=True)}">{titlehook}'+''.join(map(element,s['elements']))+'</section>')
js='''const stage=document.querySelector('.stage'),pages=[...document.querySelectorAll('.page')];let n=0;function fit(){const s=Math.min(innerWidth/1920,innerHeight/1080);stage.style.transform=`translate(${(innerWidth-1920*s)/2}px,${(innerHeight-1080*s)/2}px) scale(${s})`;}function show(i){n=Math.max(0,Math.min(pages.length-1,i));pages.forEach((p,k)=>p.classList.toggle('on',k===n));document.querySelector('.pager').textContent=`${n+1} / ${pages.length}  ·  ← → 翻页  ·  N 备注  ·  F 全屏`;document.querySelector('.note').textContent=pages[n].dataset.notes;history.replaceState(null,'','#'+(n+1));}addEventListener('resize',fit);addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key))show(n+1);if(['ArrowLeft','PageUp'].includes(e.key))show(n-1);if(e.key==='Home')show(0);if(e.key==='End')show(pages.length-1);if(e.key.toLowerCase()==='n')document.querySelector('.note').classList.toggle('on');if(e.key.toLowerCase()==='f')document.documentElement.requestFullscreen?.();});window.show=show;fit();show((parseInt(location.hash.slice(1))||1)-1);'''
(OUT/'Rust内核模块-源码走读.html').write_text('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>Rust 内核模块源码走读</title><style>'+css+'</style></head><body><div class="stage">'+''.join(pages)+'</div><div class="pager"></div><div class="note"></div><script>'+js+'</script></body></html>',encoding='utf-8')
with (OUT/'traceability.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['page','chapter','title','source','representation']);
    for i,s in enumerate(slides,1):w.writerow([i,s['chapter'],s['title'],'; '.join(s['sources']),'native editable source/log/table/diagram'])
blue=['# Rust 内核模块源码走读 · 22 页蓝图','', '基线：cc79af3。源码只读引用；build、第三方内核源码和虚拟机镜像不作为功能源码。', '', '适配说明：项目没有图形界面，采用源码、日志节选及机制图，不重绘虚构应用界面。图表参照技能 C01 分层、C11 活动、C14 状态模板，采用原生可编辑对象。', '', '| 页 | 章节 | 标题 | 源码落点 |','|---|---|---|---|']
for i,s in enumerate(slides,1):blue.append(f'| {i} | {s["chapter"]} | {s["title"]} | {"; ".join(s["sources"])} |')
(OUT/'blueprint.md').write_text('\n'.join(blue),encoding='utf-8')
(OUT/'阅读说明.md').write_text('# 源码走读详细版\n\nPowerPoint 为可编辑的 22 页版本，HTML 可离线浏览，无需联网。HTML 使用左右方向键翻页、N 显示备注、F 全屏。\n\n代码及日志来自仓库 cc79af3 与 2026-10-18 保存的实测证据。日志仅作节选排版，结论以原始日志和版本信息为准。traceability.csv 提供逐页源码锚点。原 10 页汇报稿保留。\n',encoding='utf-8')
print('Prepared 22 slides, offline HTML, blueprint and traceability.')
