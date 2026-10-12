# Page Control Skill — Claude

Skill adaptativa para **Claude Code (terminal e web)** e **Claude App / claude.ai**. Analisa projetos web e cria sistemas de controle configurável, desde overlays ocultos em HTML standalone até páginas administrativas completas com Firestore.

## O que ela faz

A capacidade principal é `CREATE`: quando o projeto ainda não possui painel ou Admin, a skill lê o projeto, descobre recursos controláveis, recomenda uma arquitetura, apresenta a configuração quando necessário e depois implementa. Também suporta `ADAPT`, `MIGRATE` e `AUDIT`.

Ela conhece, entre outros:

- overlay/painel oculto, drawer, full-screen e editor contextual;
- página `admin.html` ou rota Admin separada;
- arquitetura híbrida Admin + preview;
- textos, números, Splash, timers, efeitos, imagens responsivas, cards e visibilidade;
- localStorage, import/export JSON, configuração estática, IndexedDB, Firestore e backend existente;
- sincronização local ou reativa, inclusive Firestore `onSnapshot`;
- defaults, reset, restore, validação, autenticação/autorização e regras de segurança quando necessárias.

## Conteúdo

```
page-control/
├── SKILL.md                              instruções centrais e gatilho
├── scripts/inspect_project.py            levantamento mecânico do projeto
├── references/                           conhecimento carregado sob demanda
├── assets/config-proposal-template.md    template da configuração proposta
├── examples/                             dois casos de referência
└── evals/trigger-eval.json               casos de ativação executáveis
```

## Instalação

### Claude Code — por projeto (recomendado)

```text
<repo>/.claude/skills/page-control/SKILL.md
```

É a única forma que funciona nas **sessões web**, porque o container clona o repositório do zero a cada sessão. Precisa estar commitado.

### Claude Code — pessoal

```text
~/.claude/skills/page-control/SKILL.md
```

Vale em todos os seus projetos no terminal local. Não aparece nas sessões web.

### Claude App / claude.ai

Compacte a pasta `page-control` em `.zip` e envie em **Configurações → Capacidades → Skills**. Requer execução de código habilitada na conta.

O envio é feito pelo desktop ou pelo navegador. O **app Android consome** a skill já habilitada na conta, mas não permite criá-la nem enviá-la.

## Uso

```text
/page-control Preciso de um painel oculto neste HTML.
/page-control Preciso de uma página Admin para este projeto.
/page-control Quero controle para esse projeto; analise e recomende.
/page-control Migre esse painel para Firestore.
```

A invocação explícita não é necessária — a descrição em `SKILL.md` dispara a skill automaticamente quando o pedido corresponder, inclusive em pedidos que não usam as palavras "admin" ou "painel".

O comportamento padrão é inspecionar o projeto, propor a configuração quando houver decisões abertas e implementar após aprovação. Se o pedido já contiver as decisões necessárias e solicitar execução direta, a skill segue sem entrevista redundante.

## Inspeção mecânica

O passo 1 da skill é padronizado por um script, para não refazer a mesma varredura à mão a cada projeto:

```bash
python3 scripts/inspect_project.py <diretorio-ou-arquivo-html>
```

Emite JSON com arquivos, tecnologias, sinais de persistência (`localStorage`, `IndexedDB`, Firebase/Firestore), indícios de Admin/overlay existente, funções de renderização e restrições como single-file. Aceita um diretório **ou** um único HTML, o que o torna utilizável também no app de chat, onde só existe o anexo da conversa. Depende apenas da biblioteca padrão do Python 3.

## Calibrar o disparo

```bash
# a partir do diretório do skill-creator
python -m scripts.run_loop \
  --eval-set <caminho>/page-control/evals/trigger-eval.json \
  --skill-path <caminho>/page-control \
  --max-iterations 5 --verbose
```

O conjunto tem 9 positivos e 11 negativos, todos quase-acertos deliberados. O raciocínio está em `evals/activation-cases.md`.

## Compatibilidade

Segue o formato aberto Agent Skills: `SKILL.md` com frontmatter (`name`, `description`) e recursos auxiliares. O mesmo pacote serve Claude Code, Claude App e Claude API/Agent SDK — a skill define *como* analisar e construir; a superfície define *quais arquivos e permissões* existem para executar. Ver `references/claude-runtime.md`.

---

## ⚠️ Arquivos pendentes de restauração

Esta cópia foi reconstruída a partir das correções de auditoria. Os arquivos
abaixo são os **originais do pacote** e não foram alterados pela auditoria —
copie-os do seu `.zip` para completar a skill:

```
references/profile.md
references/project-inspection.md
references/control-discovery.md
references/embedded-control.md
references/admin-page.md
references/persistence-sync.md
references/firestore-security.md
references/guided-setup.md
references/validation.md
assets/config-proposal-template.md
examples/standalone-overlay.md
examples/admin-firestore.md
```

O `SKILL.md` aponta para todos eles. Enquanto não estiverem no lugar, a skill
dispara e executa o fluxo principal, mas os passos que dependem de referência
detalhada ficam sem o aprofundamento.
