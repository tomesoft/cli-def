
# cli-def TOML Specification v0.1

## 1. Overview

cli-def は TOML により CLI 構造を宣言的に定義する DSL である。

CLI 定義は以下の変換を経て実行される：

```text
TOML → CliDef (AST) → Builder → Runtime → Execution
```

## 2. Root Structure

```toml
[cli]
key = "MyCLI"
help = "Description"
prompt = "mycli> "
```

- `[cli]` は必須
- CLI のルート定義

### 2.1 Fields

|field|type|required|description
|---|---|---|---
|key|str|required|CLI名
|help|str|optional|ヘルプ
|prompt|str|optional|repl実行時のプロンプト文字列

## 3. Command Definition

```toml
[cli.command]
help = "Description"
args = [...]
entrypoint = "module:function"
```

- Command Definitionにおいては `[cli.<command>]`の`<command>`部分が key として扱われる
- `[cli.<command>.<subcommand>]` のようにサブコマンドも定義可能

### 3.1 Fields

|field|type|required|description
|---|---|---|---
|help|str|optional|ヘルプ
|args|list|optional|引数定義
|entrypoint|str|optional|実行関数
|inherit_from|list[str]|optional|継承元
|bind|table|optional|パラメータ固定

## 4. Argument Definition

```toml
args = [
  {key="name", mult="?", type="str"},
  {key="upper", option="--upper", aliases=["-U"], is_flag=true, default=false},
  {key="plan", option="--plan", choices=["A", "B", "C"], default="A"},
]
```

### 4.1 Fields

|field|type|required|description
|---|---|---|---
|key|str|required|パラメータ名
|mult|str|optional|"1", "?", "*" 省略時のデフォルトについては後述
|type|str|optional|str, int など
|option|str|optional|CLIオプション (指定がない場合には positional argument として扱う)
|aliases|list[str]|optional|オプションの別名(典型的にはshort version)
|is_flag|bool|optional|trueならフラグ(*1)
|choices|list[Any]|optional|選択肢リスト
|default|Any|optional|デフォルト値
|help|str|optional|ヘルプ

(*1) If is_flag is true:

- type is implicitly bool
- mult must be "1"

### 4.2 mult

mult 指定省略時は、以下のルールで決定する

- positional argument の場合 `1..1`
- optional argument の場合 `0..1`

If mult is not specified, it is inferred as follows:

- Positional arguments:
    mult = "1..1"

- Optional arguments (option is specified):
    mult = "0..1"

The presence of a default value does not affect multiplicity.

A future extension may allow explicit required specification.

## 5. Inheritance

```toml
[cli.child]
inherit_from = ["parent"]
```

### 5.1 Rules

- (keyが一致する *1)親の定義を継承する
- child が指定したフィールドは上書きされる
- 複数継承は順序適用（後勝ち）

(*1) inherit_from refers to command keys within the same CLI namespace.  
Each entry must refer to an existing command key.  
Resolution is based on defpath

Only leaf commands (commands without subcommands) can be used as inheritance sources.

Commands that define subcommands are considered containers and cannot be inherited from.

Attempting to inherit from a non-leaf command results in an error.

If inherit_from is not specified, templates are applied implicitly

### 5.2 Inheritance Order

When multiple inheritance sources are specified:

    inherit_from = ["A", "B", "C"]

The resolution order is:

    A → B → C → child

Later entries override earlier ones.

### 5.3 Inheritance Level

Inheritance is resolved only one level deep.

Transitive inheritance is not applied.

## 6. Parameter Binding（Partial Application）

```toml
[cli.greet-john]
inherit_from = ["greet"]
bind = {name = "John"}
```

### 6.1 Fields

|field|type|required|description
|---|---|---|---
|bind|table[str, Any]|optional|値バインド辞書

### 6.2 Semantics

- `bind` はコマンドのパラメータを固定する
- 実行時のパラメータとマージされる

### 6.3 Merge Rule

```python
final_params = merge(runtime_params, bound_params)
```

final_params is constructed as follows:

1. Start from runtime_params
2. For each key in bound_params:
   - override runtime_params[key] with bound_params[key]
3. Result is final_params

### 6.4 Override Policy

デフォルト：bind が優先（override不可）

### 6.5 Type Rules

|mult|bind value
|---|---
|"1"|scalar
|"?"|scalar or null
|"*"|list

### 6.6 Inheritance with bind

```toml
parent.bind + child.bind → child優先でマージ
```

- bind keys must correspond to defined arguments
- bind values must satisfy argument type constraints
- bind values must satisfy mult constraints

## 7. Entrypoint Resolution

```toml
entrypoint = "module:function"
```

### 7.1 Rules

- 指定されていればそれを使用
- 未指定の場合、親から継承
- If no entrypoint is resolved after inheritance, the command is handled by fallback handler

## 8. defpath

構造上の各ノードの`key`を`/`で連結したものを `defpath` (definition path) とする  
 `/MyCLI/command/arg` のように表現し、定義上のノードを一意に指し示すことができる

defpath is used as a unique identifier for commands and is used for:

- handler binding
- command resolution
- runtime dispatch

## 9. Resolution Model

cli-def defines two representations:

- Raw definition: as written in TOML
- Resolved definition: fully expanded, used for execution

Runtime and builders operate only on resolved definitions.

## 10. Execution Model

CLI実行時：

1. Parse CLI arguments into runtime_params
2. Resolve command definition (including inheritance)
3. Apply parameter binding to produce final_params
4. Construct CliEvent
5. Dispatch event to handler

## 11. REPL

```bash
cli-def repl
```

- コマンドを逐次実行
- 結果は内部ストアに保存

## 12. Reserved Commands

- `_` で始まるコマンドは内部用途、command template(あるいはargumentグループ)として `inherit_from=["_template"]` から参照可能

## 13. Resolution Phase

CLI definitions are transformed into a resolved form before execution.

This process includes:

- inheritance resolution
- argument merging
- parameter binding merge
- entrypoint resolution

### 13.1 Raw vs Resolved

Raw definition:
  - preserves user input

Resolved definition:
  - fully expanded
  - used for execution


## 14. Include

The `include` field may be specified in the `[cli]` section.

Example:

```toml
    [cli]
    include = ["file1.toml", "file2.toml"]
```

Included files must also define a `[cli]` section.

Inclusion is processed in order, and later definitions override earlier ones.

The `include` field is not present in resolved definitions.


## 15. Early Parse

`_early` commands are evaluated before normal parsing.
They are not part of the resolved CLI tree.