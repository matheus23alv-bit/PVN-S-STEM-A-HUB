# Casos de ativação — Page Control

Os casos executáveis vivem em `trigger-eval.json`, no formato consumido pelo
otimizador de descrição do `skill-creator`:

```bash
# a partir do diretório do skill-creator
python -m scripts.run_loop \
  --eval-set <caminho>/evals/trigger-eval.json \
  --skill-path <caminho>/page-control \
  --max-iterations 5 --verbose
```

Este arquivo documenta o raciocínio por trás do conjunto. O JSON é a fonte da
verdade; se divergirem, o JSON vence.

## Critério dos positivos (9 casos)

Cobrem as quatro operações (`CREATE`, `ADAPT`, `MIGRATE`, `AUDIT`), os dois
modos de interação (`FAST` quando as decisões já vêm fechadas, `GUIDED` quando
o pedido é genérico) e as duas pontas de superfície (overlay embutido em
single-file e Admin separado).

O caso mais importante do conjunto é o primeiro: *"minha mãe vai ter que trocar
o preço toda semana e não sabe mexer em código"*. Não contém "admin", "painel"
nem "controle" — e é exatamente o pedido que a skill existe para atender. Se a
descrição não disparar aqui, ela falha no uso real, por melhor que vá nos casos
canônicos.

## Critério dos negativos (11 casos)

Negativo óbvio não mede nada. *"Escreva uma função fibonacci"* como negativo de
uma skill de painéis administrativos passa sempre e não informa se a descrição
está bem calibrada. Por isso todos os negativos aqui são **quase-acertos**:
compartilham vocabulário com a skill mas pedem outra coisa.

Os quatro eixos de confusão testados:

| Eixo | Exemplo | Por que não deve ativar |
|---|---|---|
| Conserto vs. construção | `TypeError` no `admin.html` | é debug pontual, não desenho de sistema de controle |
| Usuário final vs. administrador | formulário de contato no Firestore | o dado é do visitante, não configuração da página |
| Conceito vs. aplicação | Firestore vs. Realtime Database | pergunta teórica sobre tecnologia que a skill usa |
| Vizinhança semântica | "dashboard com gráfico de barras" | soa administrativo, mas é visualização (`dataviz`) |

Os dois últimos negativos (`Firebase Auth` isolado e `contenteditable` para
perfil de usuário) são os limítrofes herdados da versão anterior. Mantidos como
negativos porque, isolados, não fazem parte de um sistema Page Control —
quando fizerem, o contexto da conversa trará os sinais que justificam o
disparo.

## Como ler o resultado

Um falso negativo (positivo que não disparou) é mais grave que um falso
positivo: skill que não ativa é skill que não existe, enquanto ativação
indevida custa apenas contexto. Ao calibrar a descrição, prefira errar para o
lado de disparar mais.
