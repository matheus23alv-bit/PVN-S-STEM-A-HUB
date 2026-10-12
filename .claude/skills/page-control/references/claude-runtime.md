# Claude runtime — Page Control

## Objetivo

Adaptar a execução da Page Control Skill à superfície Anthropic sem alterar o padrão arquitetural da skill.

## Claude Code

A instalação pessoal usa `~/.claude/skills/page-control/SKILL.md`.

A instalação por projeto usa `.claude/skills/page-control/SKILL.md`.

O nome do diretório produz o comando `/page-control`. Claude Code também pode carregar a skill automaticamente quando a descrição corresponder ao pedido.

Nas sessões do Claude Code na web o container clona o repositório do zero, portanto a skill só está disponível se estiver commitada em `.claude/skills/`. Uma instalação apenas em `~/.claude/skills/` vale no terminal local, não na web.

### Comportamento esperado

1. rodar `scripts/inspect_project.py` sobre o diretório atual antes de desenhar o painel;
2. localizar HTML, CSS, JavaScript, framework, config, Firebase, Auth, estado e renderização;
3. executar `GUIDED` ou `FAST` conforme o pedido;
4. quando autorizado a implementar, editar os arquivos reais do projeto;
5. executar testes, build, lint, validação de console ou verificações adequadas quando disponíveis;
6. não instalar dependências globais sem necessidade;
7. respeitar permissões e regras do repositório.

### Invocação

```text
/page-control Preciso de um painel oculto neste HTML.
```

```text
/page-control Preciso de uma página Admin para controlar textos, imagens, cards e Splash.
```

```text
/page-control Analise o projeto e recomende a melhor arquitetura de controle.
```

## Claude App / claude.ai

A skill customizada pode ser enviada como ZIP e habilitada em Configurações → Capacidades → Skills quando a conta e a execução de código permitirem. O envio é feito pelo desktop ou pelo navegador; o app Android consome a skill já habilitada na conta, mas não permite criá-la ou enviá-la.

### Comportamento esperado

- utilizar arquivos e contexto disponibilizados na conversa/projeto;
- rodar `scripts/inspect_project.py` sobre o arquivo anexado — o script aceita um HTML único, não só um diretório;
- usar execução de código e criação de arquivos quando a superfície fornecer essas capacidades;
- não afirmar que leu arquivos locais ou repositórios que não estejam acessíveis;
- quando o projeto estiver incompleto, pedir somente os arquivos que bloqueiam materialmente a decisão;
- produzir a mesma `Configuração proposta` antes da geração quando houver decisões abertas;
- quando possível, entregar os arquivos gerados ou modificados como artefatos.

## Claude API / Agent SDK

Quando usada via API/SDK, a skill deve seguir as mesmas instruções, mas respeitar as limitações do runtime. Não assuma rede, instalação de pacotes ou acesso ao filesystem além do ambiente disponibilizado.

## Princípio

A skill define **como analisar e construir Page Control**. A superfície define **quais arquivos, ferramentas e permissões estão disponíveis para executar isso**.
