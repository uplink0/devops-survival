import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { AlertTriangle, CheckCircle2, Terminal, Cpu, MemoryStick, HardDrive, RotateCcw, Skull, ShieldAlert, Send, Clock3 } from 'lucide-react';
import './styles.css';

type Incident = {
  title: string;
  severity: string;
  icon: string;
  description: string;
  logs: string[];
  fix: string;
  damage: string;
  points: number;
  commands: Record<string, string>;
};

const incidents: Incident[] = [
  {
    title: 'CrashLoopBackOff', severity: 'CRITICAL', icon: '☠',
    description: 'payment-api перезапускается каждые 12 секунд. Прод пока жив, но уже нервничает.',
    logs: ['payment-api | Error: connection refused to postgres:5432', 'payment-api | retrying in 3s...', 'kubelet | Back-off restarting failed container'],
    fix: 'Перезапустить PostgreSQL и проверить readinessProbe.',
    damage: 'Удалить deployment payment-api. Потому что почему бы и нет.', points: 150,
    commands: {
      'kubectl get pods': 'NAME              READY   STATUS\npayment-api       0/1     CrashLoopBackOff\npostgres-0        1/1     Running\nnginx             1/1     Running',
      'kubectl logs payment-api': 'ERROR: connection refused to postgres:5432\nretrying in 3s...\nFATAL: database connection unavailable',
      'kubectl describe pod payment-api': 'Restart Count: 47\nLast State: Terminated\nReason: Error\nReadiness probe: failed',
      'kubectl get svc': 'NAME       TYPE        CLUSTER-IP\npostgres   ClusterIP   10.43.0.20\npayment    ClusterIP   10.43.0.21',
    },
  },
  {
    title: 'Disk usage 99%', severity: 'HIGH', icon: '💾',
    description: '/var/lib/docker почти закончился. Docker смотрит на тебя с осуждением.',
    logs: ['df -h /var/lib/docker', '/dev/sda1  98G  97G  0G  100% /', 'docker system df', 'Images: 18.4GB  Containers: 2.1GB'],
    fix: 'Удалить неиспользуемые Docker images/volumes и проверить логи.',
    damage: 'Скачать ещё один 8GB образ ubuntu:latest.', points: 120,
    commands: {
      'df -h': 'Filesystem      Size  Used Avail Use% Mounted on\n/dev/sda1        98G   97G     0  100% /',
      'docker system df': 'TYPE        TOTAL   ACTIVE   SIZE\nImages      18       9        18.4GB\nContainers  7        3        2.1GB\nVolumes     11       4        6.7GB',
      'docker ps': 'CONTAINER ID   IMAGE          STATUS\na81f2c         payment-api   Up 2 hours\nb12d91         nginx          Up 3 days\nc88ab3         postgres       Up 8 days',
      'du -sh /var/lib/docker/*': '12G  /var/lib/docker/overlay2\n6.7G /var/lib/docker/volumes\n2.1G /var/lib/docker/containers',
    },
  },
  {
    title: 'OOMKilled', severity: 'HIGH', icon: '🧠',
    description: 'frontend съел всю память ноды и был культурно убит Kubernetes.',
    logs: ['container frontend | memory usage: 1.98Gi', 'node | allocatable memory: 2Gi', 'reason: OOMKilled'],
    fix: 'Найти memory leak или увеличить memory limit после анализа.',
    damage: 'Поставить memory limit 128Mi и сказать «оптимизировали».', points: 130,
    commands: {
      'kubectl get pods': 'NAME              READY   STATUS\nfrontend          0/1     OOMKilled\napi               1/1     Running\npostgres           1/1     Running',
      'kubectl describe pod frontend': 'Last State: Terminated\nReason: OOMKilled\nMemory Limit: 512Mi\nPeak Usage: 1.98Gi',
      'free -h': '              total   used   free\nMem:           2.9Gi   2.8Gi   110Mi\nSwap:          512Mi   268Ki   511Mi',
      'kubectl top pod': 'NAME       CPU(cores)   MEMORY(bytes)\nfrontend   480m         1980Mi\napi        120m         420Mi',
    },
  },
  {
    title: 'Nginx 502', severity: 'MEDIUM', icon: '🌐',
    description: 'Пользователи видят 502. Backend утверждает, что он «у меня работает».',
    logs: ['nginx | connect() failed (111: Connection refused)', 'upstream: http://10.42.0.17:8000', 'GET /api/health → 502'],
    fix: 'Проверить Service endpoints и доступность backend pod.',
    damage: 'Перезапустить nginx. Три раза. Авось.', points: 100,
    commands: {
      'kubectl get pods': 'NAME              READY   STATUS\napi-7d8f          1/1     Running\nnginx-6f8d        1/1     Running\npostgres-0        1/1     Running',
      'kubectl get svc': 'NAME       TYPE        CLUSTER-IP     PORT\napi        ClusterIP   10.43.0.17     8000\nnginx      LoadBalancer 10.43.0.30   80',
      'kubectl get endpoints api': 'NAME   ENDPOINTS\napi    <none>',
      'curl localhost/api/health': 'HTTP/1.1 502 Bad Gateway\nServer: nginx',
    },
  },
  {
    title: 'Certificate expires in 3h', severity: 'MEDIUM', icon: '🔐',
    description: 'TLS-сертификат скоро превратится в тыкву.',
    logs: ['openssl x509 -enddate', 'notAfter=Sep 05 22:17:00 2026 GMT', 'issuer=Let’s Encrypt'],
    fix: 'Продлить сертификат и проверить автоматическую ротацию.',
    damage: 'Отключить HTTPS «временно».', points: 90,
    commands: {
      'openssl x509 -enddate': 'notAfter=Sep 05 22:17:00 2026 GMT',
      'kubectl get certificate': 'NAME       READY   SECRET\nproduction False   production-tls',
      'kubectl describe certificate production': 'Status: False\nReason: RenewalFailed\nMessage: ACME challenge failed',
      'curl -I https://production.local': 'HTTP/2 200\nserver: traefik\nstrict-transport-security: max-age=31536000',
    },
  },
];

const genericCommands: Record<string, string> = {
  clear: '',
  help: 'Доступные команды: kubectl get pods | kubectl logs <pod> | kubectl describe pod <pod> | kubectl get svc | kubectl get endpoints <svc> | kubectl top pod | docker ps | docker system df | df -h | du -sh /var/lib/docker/* | free -h | curl localhost/api/health | openssl x509 -enddate',
  whoami: 'ivan',
  pwd: '/home/ivan',
  'date': 'Sat Sep 05 2026 17:00:00 MSK',
};

function App() {
  const [idx, setIdx] = useState(0);
  const [score, setScore] = useState(0);
  const [health, setHealth] = useState(100);
  const [solved, setSolved] = useState(false);
  const [history, setHistory] = useState<string[]>([]);
  const [command, setCommand] = useState('');
  const [terminalLines, setTerminalLines] = useState<string[]>([]);
  const [streak, setStreak] = useState(0);

  const inc = incidents[idx];
  const stats = useMemo(() => ({
    cpu: Math.min(98, 38 + idx * 11 + (solved ? 8 : 0)),
    ram: Math.min(97, 54 + idx * 7 + (solved ? -10 : 0)),
    disk: solved && idx === 1 ? 72 : idx === 1 ? 99 : 61 + idx * 8,
    pods: solved || idx !== 0 ? '15/15' : '14/15',
  }), [idx, solved]);

  const addHistory = (message: string) => setHistory(h => [message, ...h].slice(0, 7));

  const solve = () => {
    if (solved) return;
    setScore(s => s + inc.points);
    setSolved(true);
    setStreak(s => s + 1);
    addHistory(`${inc.title} — RESOLVED +${inc.points}`);
    setTerminalLines(lines => [...lines, '', '✓ Incident resolved.', `+${inc.points} XP`, 'Production stabilized.']);
  };

  const worsen = () => {
    const damage = 20;
    setHealth(h => Math.max(0, h - damage));
    setStreak(0);
    addHistory(`Ты сделал хуже: ${inc.title} -${damage} HEALTH`);
    setTerminalLines(lines => [...lines, '', '⚠ WRONG ACTION', inc.damage, `Health -${damage}`]);
  };

  const next = () => {
    setIdx(i => (i + 1) % incidents.length);
    setSolved(false);
    setCommand('');
    setTerminalLines([]);
  };

  const runCommand = () => {
    const input = command.trim().replace(/\s+/g, ' ');
    if (!input) return;
    const normalized = input.toLowerCase();
    let output = genericCommands[normalized];
    if (output === undefined) {
      const exact = Object.entries(inc.commands).find(([key]) => normalized === key.toLowerCase());
      if (exact) output = exact[1];
    }
    if (output === undefined && normalized.startsWith('kubectl logs ')) {
      const pod = input.slice('kubectl logs '.length).trim();
      output = inc.commands['kubectl logs payment-api'] && pod.includes('payment')
        ? inc.commands['kubectl logs payment-api']
        : `No logs found for pod "${pod}" in namespace production.`;
    }
    if (output === undefined && normalized.startsWith('kubectl describe pod ')) {
      const pod = input.slice('kubectl describe pod '.length).trim();
      const known = Object.entries(inc.commands).find(([key]) => key.startsWith('kubectl describe pod') && pod && key.toLowerCase().includes(pod.toLowerCase()));
      output = known ? known[1] : `Name: ${pod}\nStatus: Running\nNo additional events.`;
    }
    if (output === undefined) output = `bash: ${input}: command not found\nType "help" to see available commands.`;
    if (normalized === 'clear') {
      setTerminalLines([]);
    } else {
      setTerminalLines(lines => [...lines, `ivan@production:~$ ${input}`, ...output.split('\n')]);
    }
    setCommand('');
  };

  return <div className="app">
    <header>
      <div className="brand"><div className="logo">⌘</div><div><b>DEVOPS SURVIVAL</b><span>production incident simulator</span></div></div>
      <div className="top"><span>HEALTH <strong>{health}%</strong></span><span>SCORE <strong>{score}</strong></span><span>STREAK <strong>{streak}</strong></span></div>
    </header>
    <main>
      <section className="metrics">
        <Metric icon={<Cpu/>} label="CPU" value={stats.cpu} unit="%"/>
        <Metric icon={<MemoryStick/>} label="RAM" value={stats.ram} unit="%"/>
        <Metric icon={<HardDrive/>} label="DISK" value={stats.disk} unit="%"/>
        <div className="metric pods"><span className="mi">☸</span><div><small>PODS</small><b>{stats.pods}</b></div></div>
      </section>

      <section className="grid">
        <div className="incident card">
          <div className="incident-head"><span className="badge">{inc.severity}</span><span className="id">INC-{String(idx + 1).padStart(4, '0')}</span></div>
          <div className="title"><span>{inc.icon}</span><div><h1>{inc.title}</h1><p>{inc.description}</p></div></div>

          <div className="terminal incident-log">
            <div className="term-head"><Terminal size={15}/> incident.log <span>LIVE</span></div>
            {inc.logs.map((l, i) => <div className="log" key={i}><i>{i + 1}</i>{l}</div>)}
          </div>

          <div className="terminal player-terminal">
            <div className="term-head"><Terminal size={15}/> production-shell <span><Clock3 size={12}/> INTERACTIVE</span></div>
            <div className="terminal-output">
              {!terminalLines.length && <div className="terminal-placeholder">Type <b>help</b> to see available commands. Investigate the incident before acting.</div>}
              {terminalLines.map((line, i) => <div className={line.startsWith('✓') ? 'terminal-success' : line.startsWith('⚠') ? 'terminal-warning' : ''} key={i}>{line || '\u00a0'}</div>)}
            </div>
            <div className="command-row">
              <span>ivan@production:~$</span>
              <input value={command} onChange={e => setCommand(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') runCommand(); }} placeholder="kubectl get pods" autoComplete="off" spellCheck={false}/>
              <button onClick={runCommand} aria-label="Run command"><Send size={15}/></button>
            </div>
          </div>

          <div className="actions">
            <button className="fix" onClick={solve} disabled={solved}><CheckCircle2/> {solved ? 'ПОЧИНЕНО' : 'ПОЧИНИТЬ'}</button>
            <button className="bad" onClick={worsen}><Skull/> СДЕЛАТЬ ХУЖЕ</button>
          </div>
          {solved && <div className="success"><CheckCircle2/> Инцидент закрыт. Production снова делает вид, что всё нормально.</div>}
          <div className="hint"><ShieldAlert/> <b>Подсказка:</b> {inc.fix}</div>
        </div>

        <aside>
          <div className="card side"><h3>MISSION CONTROL</h3><div className="mission"><span>Incident</span><b>{idx + 1} / {incidents.length}</b></div><div className="bar"><i style={{width: `${((idx + 1) / incidents.length) * 100}%`}}/></div><button className="next" onClick={next}><RotateCcw/> Следующий инцидент</button></div>
          <div className="card side history"><h3>EVENT LOG</h3>{history.length ? history.map((x, i) => <div className="event" key={i}><span>›</span>{x}</div>) : <div className="empty">Лог пуст. Пока ты ничего не сломал.</div>}</div>
          <div className="card side command-help"><h3>QUICK COMMANDS</h3><code>kubectl get pods</code><code>kubectl logs &lt;pod&gt;</code><code>kubectl describe pod &lt;pod&gt;</code><code>kubectl get svc</code><code>docker ps</code><code>df -h</code><code>free -h</code></div>
          <div className="quote"><AlertTriangle size={13}/> «Это не баг. Это незадокументированная фича.»<small>— любой DevOps в 03:47</small></div>
        </aside>
      </section>
    </main>
  </div>;
}

function Metric({icon, label, value, unit}: {icon: React.ReactNode; label: string; value: number; unit: string}) {
  return <div className="metric"><span className="mi">{icon}</span><div><small>{label}</small><b>{value}{unit}</b></div><div className="mini"><i style={{width: `${value}%`}}/></div></div>;
}

createRoot(document.getElementById('root')!).render(<App/>);
