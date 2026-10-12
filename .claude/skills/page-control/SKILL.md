---
name: page-control
description: >
  Analisa projetos web e cria, adapta, migra ou audita sistemas de controle
  configurável de páginas. Use quando o usuário pedir painel oculto/overlay,
  editor embutido, página admin/admin.html, controle de
  textos/valores/imagens/cards/efeitos/Splash, persistência
  local/JSON/Firestore, sincronização reativa, ou quando quiser aplicar um
  padrão de administração a um projeto que ainda não possui painel — inclusive
  quando não usar as palavras "admin" ou "painel", como em "quero poder editar
  os textos dessa página sem mexer no código" ou "preciso trocar essa imagem e
  o preço sem abrir o HTML". Inspecione o projeto antes de propor ou
  implementar e preserve a arquitetura existente.
---

# Page Control

## Finalidade

Criar e manter sistemas de controle configurável de páginas sem obrigar o usuário a redescrever, projeto por projeto, toda a arquitetura administrativa.

A capacidade principal é `CREATE`: construir um sistema de controle quando o projeto ainda não possui painel ou página administrativa. Também opere em `ADAPT`, `MIGRATE` e `AUDIT` quando o contexto exigir.

## Princípios

Estes princípios existem porque sistemas de controle falham de maneiras previsíveis. Entender o motivo de cada um permite generalizar para casos que esta skill não previu.

**Inspecione antes de projetar, e reutilize antes de criar.** Um painel desenhado sem ler o projeto quase sempre duplica estado ou renderização que já existia. Quando existem duas fontes de verdade para o mesmo valor, elas divergem — e o bug resultante aparece só em produção, no caminho que ninguém testou. Preserve a arquitetura e os contratos existentes sempre que forem tecnicamente adequados.

**Prefira controlar estado/configuração e reutilizar a renderização existente.** Se a aplicação já tem uma via normal de atualizar a tela, o painel deve alimentar essa via, não abrir uma segunda. Painel que redesenha a página por conta própria passa a mostrar algo diferente do que o usuário final vê.

**Não transforme toda propriedade visual em configuração editável.** Um painel que expõe `padding`, seletores internos e IDs técnicos fica inutilizável para quem não é desenvolvedor — exatamente o público para quem o painel foi feito. Exponha o que tem significado administrativo; o resto permanece no código.

**Ocultação de interface nunca equivale a segurança.** Triplo clique, hotspot, long press e rota escondida são descoberta/UX. Quem souber a sequência entra, e o código está no cliente. Se o dado precisa de proteção, a proteção é autenticação e autorização reais.

**Mantenha a solução proporcional ao problema e recomende sem impor.** Um HTML single-file não precisa de RBAC, audit trail e publishing. Quando houver mais de um caminho válido, compare e aponte um principal — a decisão arquitetural é do usuário, não sua.

**Não pergunte o que já está respondido.** Se o pedido ou o projeto já contêm a informação, perguntar de novo transfere para o usuário um trabalho que é seu.

Leia `references/profile.md` sempre que a tarefa for `CREATE` ou quando o usuário pedir para aplicar o padrão de controle do projeto.

## Superfície de execução

Identifique onde você está rodando antes de agir, porque isso define quais arquivos existem — não o que a skill sabe fazer.

Em **Claude Code** (terminal ou web) há um diretório de trabalho: explore o codebase antes de editar e use as ferramentas do projeto para validar. Em **Claude App / claude.ai** só existem os arquivos da conversa e o sandbox de execução: nunca afirme ter lido um repositório que não foi fornecido; quando a implementação direta for impossível por falta de acesso, entregue a configuração e os arquivos geráveis e diga exatamente o que falta.

Não confunda capacidade da skill com permissão do ambiente. Leia `references/claude-runtime.md` em caso de dúvida sobre instalação, escopo ou limitações da superfície.

## Modos de operação

Determine um modo principal antes de planejar alterações:

- `CREATE`: não existe sistema de controle adequado; criar um.
- `ADAPT`: já existe painel, estado, configuração, persistência ou Admin; estender preservando o que funciona.
- `MIGRATE`: existe implementação antiga, desorganizada ou incompatível; mapear contratos e migrar com recuperação.
- `AUDIT`: analisar sem necessariamente modificar arquivos.

Um projeto pode ter operações secundárias. Exemplo: `ADAPT` como modo principal e `MIGRATE` para substituir localStorage por Firestore.

## Modos de interação

### FAST

Use quando o usuário já determinou decisões materiais, por exemplo:

- "crie um painel oculto neste HTML";
- "crie uma página admin para controlar textos e preços";
- "use Firestore e triplo clique".

Não repita perguntas já respondidas. Inspecione, valide compatibilidade, apresente impacto conciso e implemente se o usuário pediu execução direta.

### GUIDED

Use quando o objetivo for genérico ou houver decisões arquiteturais materiais ainda abertas, por exemplo:

- "quero controle para este projeto";
- "aplique meu padrão de administração".

Fluxo:

1. inspecionar;
2. modelar o projeto;
3. detectar candidatos de controle;
4. recomendar uma arquitetura principal;
5. apresentar somente alternativas relevantes;
6. produzir uma configuração proposta;
7. perguntar apenas decisões que alterem materialmente a solução;
8. aguardar aprovação para gerar, salvo ordem explícita de implementação imediata.

Leia `references/guided-setup.md` quando estiver em GUIDED.

## Processo operacional

### 1. Inspecionar

Comece pelo levantamento mecânico, que é sempre o mesmo e não merece ser refeito à mão a cada projeto:

```bash
python3 scripts/inspect_project.py <caminho-do-projeto-ou-arquivo>
```

O script emite um JSON com arquivos, tecnologias detectadas, sinais de persistência (`localStorage`, `IndexedDB`, Firebase/Firestore), indícios de Admin/overlay já existente, funções de renderização e restrições como single-file. Ele funciona tanto sobre um diretório quanto sobre um único HTML anexado, o que o torna utilizável nas três superfícies. Use a saída como ponto de partida e leia os arquivos que ela apontar como relevantes.

Interprete o resultado — o script detecta, não decide. Procure então:

- HTML/páginas/rotas;
- CSS e tokens visuais;
- JavaScript e event handlers;
- estado central, stores, objetos de configuração e defaults;
- funções de renderização/atualização;
- localStorage, IndexedDB, arquivos de configuração, API, Firebase/Firestore;
- autenticação e autorização;
- Admin, overlays, modais ou ferramentas internas existentes;
- estruturas repetíveis como cards/listas;
- Splash, timers, animações, transições e efeitos;
- uploads/imagens;
- usuários, mensagens, atendimento ou fluxos operacionais;
- restrições como single-file, hospedagem estática ou compatibilidade legada.

Não assuma que ausência em um arquivo significa ausência no projeto inteiro quando existirem imports ou referências para outros arquivos.

Leia `references/project-inspection.md` para inspeções não triviais.

### 2. Modelar o projeto

Construa um modelo resumido antes de recomendar. Identifique, quando aplicável:

- `operationMode`;
- tipo de projeto e arquitetura;
- estrutura de arquivos;
- tecnologias/dependências;
- backend;
- persistência;
- autenticação/autorização;
- sincronização;
- sistema administrativo existente;
- recursos já configuráveis;
- áreas candidatas a controle;
- invariantes/restrições;
- riscos de integração.

Esse modelo pode permanecer interno. Mostre-o somente quando útil para decisão ou auditoria.

### 3. Detectar candidatos a controle

Não espere o usuário listar campo por campo. Analise o domínio e identifique bons candidatos.

Sempre procure, quando existirem no projeto:

- textos: títulos, labels, mensagens, CTAs, termos;
- valores numéricos: preços, saldos, percentuais, metas, limites;
- timing: segundos, delays, duração, intervalos, auto-hide;
- Splash: duração, ativação, textos, mídia e efeitos quando presentes;
- efeitos: duração, delay, intensidade/preset e estados de efeitos existentes;
- imagens: troca/upload/URL, preview e ajuste responsivo;
- cards/listas: criar, editar, remover, ordenar, ativar/desativar;
- visibilidade: seções, banners, avisos, componentes;
- comportamento: feature flags, destinos, estados operacionais e parâmetros de fluxo;
- atendimento: somente quando houver domínio compatível ou solicitação explícita.

Classifique cada candidato em `conteudo`, `visual`, `funcional` ou `estrutural`.

Não exponha automaticamente margens, paddings, seletores internos, IDs técnicos ou qualquer detalhe sem significado administrativo.

Leia `references/control-discovery.md` para regras de seleção, imagens, cards, efeitos e atendimento.

### 4. Escolher a superfície de controle

Superfícies suportadas:

- `embedded-overlay` — overlay/painel oculto embutido;
- `embedded-drawer` — painel lateral;
- `embedded-fullscreen` — editor full-screen;
- `contextual-editor` — editor no próprio contexto visual;
- `separate-admin` — página/rota administrativa separada;
- `hybrid` — Admin separado + preview/editor contextual.

Se o usuário já escolheu a superfície, respeite-a salvo incompatibilidade concreta.

Se não escolheu, recomende conforme escopo, número de módulos, necessidade multiusuário, volume de dados e benefício do contexto visual.

Leia `references/embedded-control.md` para controles embutidos e `references/admin-page.md` para Admin separado/híbrido.

Para ver as duas pontas do espectro aplicadas a projetos concretos, leia `examples/standalone-overlay.md` (overlay oculto em HTML single-file) e `examples/admin-firestore.md` (Admin separado com Firestore e sync reativo). São fontes de capacidade, não templates para copiar.

### 5. Escolher estado, persistência e sincronização separadamente

Não acople interface e persistência.

Estado pode ser:

- objeto/config local;
- store existente;
- state de framework;
- draft separado;
- estado por usuário/entidade.

Persistência pode ser:

- nenhuma;
- memória;
- localStorage;
- IndexedDB;
- arquivo import/export;
- configuração estática;
- Firestore;
- API/backend existente;
- adapter já presente no projeto.

JSON é formato de serialização, não backend remoto por si só.

Sincronização pode ser:

- render local;
- save-and-render;
- `storage` event;
- listener reativo existente;
- Firestore `onSnapshot`;
- mecanismo nativo do framework/backend.

Leia `references/persistence-sync.md` quando houver decisão de persistência/sync.

### 6. Segurança

Separe:

- discovery: como o painel é encontrado;
- authentication: quem é o usuário;
- authorization: o que pode fazer;
- validation: quais dados são aceitos;
- data protection: onde segredos/dados sensíveis podem existir;
- audit: rastreabilidade quando necessária.

Triplo clique, hotspot, long press, atalho ou rota escondida são apenas discovery/UX.

Senha hardcoded em JavaScript não é autenticação robusta.

Se usar Firestore em contexto que exige proteção, avalie Firebase Auth e Security Rules; não dependa somente do frontend.

Leia `references/firestore-security.md` para Firestore, autenticação, Rules, HTML controlado e sanitização.

### 7. Recomendar e configurar

Conheça muitas capacidades, mas ofereça somente as relevantes:

`KNOWN → COMPATIBLE → RELEVANT → OFFERED`

Quando houver mais de uma alternativa válida, compare no mínimo:

- impacto;
- complexidade;
- código/dependências adicionadas;
- manutenção;
- persistência e multi-device;
- sincronização;
- segurança;
- reversibilidade;
- compatibilidade;
- risco de migração;
- necessidade real.

Produza uma `Configuração proposta` usando `assets/config-proposal-template.md` quando o usuário ainda precisar aprovar a arquitetura.

A recomendação deve ter uma opção principal e, no máximo, alternativas materialmente relevantes.

### 8. Analisar impacto

Antes de implementar, determine:

- arquivos que serão alterados;
- arquivos que serão criados;
- infraestrutura/dependências adicionadas;
- persistência e schema afetados;
- riscos;
- compatibilidade;
- reversibilidade.

Para projetos simples, mantenha isso curto.

### 9. Implementar

Somente após arquitetura suficientemente compreendida.

Regras:

- reutilize funções de renderização e estado existentes;
- não crie uma segunda lógica de UI quando a aplicação já possui uma via normal de atualização;
- use manipulação direta do DOM quando ela for coerente com um standalone simples/editor contextual;
- preserve defaults e compatibilidade quando existentes;
- prefira merges/updates seletivos a substituições destrutivas quando houver schema evolutivo;
- mantenha IDs, classes e contratos públicos estáveis quando possível;
- não introduza backend, realtime, RBAC, audit trail, migrations ou publishing sem necessidade;
- não exponha segredos no cliente;
- não grave HTML arbitrário sem avaliar sanitização e autorização.

### 10. Validar

A implementação não está concluída até validar, quando aplicável:

- página funciona sem abrir o painel;
- funcionalidades anteriores continuam operacionais;
- controles alteram somente o escopo previsto;
- defaults/reset/restore funcionam;
- persistência sobrevive ao reload quando esperado;
- preview corresponde ao resultado;
- dados inválidos são rejeitados/normalizados;
- erros de persistência são tratados;
- sync não cria loops nem sobrescritas inesperadas;
- autenticação/autorização/Rules continuam válidas;
- import/export preserva schema;
- console não ganhou novos erros;
- configuração antiga permanece compatível quando prometido;
- reversão é possível quando exigida.

Para Firestore, múltiplos usuários, migração, draft/publicado ou rollback, carregue `references/validation.md` e execute as verificações adicionais adequadas.

## Saídas esperadas

### Quando o usuário ainda não aprovou a arquitetura

Entregue:

1. leitura resumida do projeto;
2. controles detectados;
3. recomendação principal;
4. alternativas relevantes;
5. configuração proposta;
6. impacto esperado;
7. somente perguntas materiais ainda abertas.

Não implemente até aprovação, salvo solicitação explícita de execução direta.

### Quando o usuário pediu implementação direta

Entregue:

1. resumo da leitura;
2. arquitetura escolhida e justificativa curta;
3. alterações realizadas;
4. validações executadas;
5. riscos ou revisão humana ainda necessária.

## Regras de perfil

O perfil de referência foi extraído de projetos com overlays ocultos, editores standalone, páginas Admin modulares, localStorage, import/export, Firestore e listeners realtime. Esses exemplos são fontes de capacidade, não templates rígidos.

Classifique padrões aprendidos como:

- `RECORRENTE` — aparece em vários projetos e é candidato a padrão;
- `VARIÁVEL` — deve permanecer opção/capacidade;
- `ESPECÍFICO` — pertence ao domínio de um projeto;
- `LEGADO/DEFICIENTE` — recorrente, mas tecnicamente inadequado para ser promovido.

Frequência não prova qualidade arquitetural.

## Referências sob demanda

- Perfil e convenções: `references/profile.md`
- Inspeção e modelagem: `references/project-inspection.md`
- Descoberta de controles: `references/control-discovery.md`
- Painel oculto/embutido: `references/embedded-control.md`
- Página Admin/híbrida: `references/admin-page.md`
- Persistência e sync: `references/persistence-sync.md`
- Firestore e segurança: `references/firestore-security.md`
- Entrevista/configuração: `references/guided-setup.md`
- Validação: `references/validation.md`
- Execução no Claude Code/App: `references/claude-runtime.md`

## Critério de sucesso

A skill cumpriu seu objetivo quando o usuário consegue chegar com um projeto novo sem Admin e dizer apenas algo como:

- "preciso de um painel oculto neste HTML";
- "preciso de uma página Admin para este projeto";
- "quero controle para este projeto; escolha a melhor arquitetura";

...e o agente consegue entender o projeto, descobrir o que faz sentido controlar, propor uma configuração compatível e criar o sistema sem exigir que o usuário reexplique do zero o padrão administrativo a cada projeto.
