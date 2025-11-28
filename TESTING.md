# 测试策略文档

本项目采用分层测试策略，将单元测试和集成测试分离，以提高CI/CD效率和测试可靠性。

## 测试分类

### 1. 单元测试（Unit Tests）

**文件命名：** `*.test.ts`

**特点：**
- 不依赖外部服务（数据库、API、Python脚本等）
- 执行速度快（< 1秒）
- 可在任何环境运行（本地、CI）
- 使用mock数据和stub函数

**示例：**
```typescript
// server/auth.logout.test.ts
describe("auth.logout", () => {
  it("clears the session cookie and reports success", async () => {
    const { ctx, clearedCookies } = createAuthContext();
    const caller = appRouter.createCaller(ctx);
    const result = await caller.auth.logout();
    
    expect(result).toEqual({ success: true });
    expect(clearedCookies).toHaveLength(1);
  });
});
```

### 2. 集成测试（Integration Tests）

**文件命名：** `*.integration.test.ts`

**特点：**
- 依赖外部服务（数据库、Python脚本、API）
- 执行速度较慢（> 5秒）
- 需要特定环境配置
- 测试真实的端到端流程

**示例：**
```typescript
// server/strategy.backtest.integration.test.ts
describe("strategy.backtest integration", () => {
  it("should run real backtest with Python script", async () => {
    const ctx = createTestContext();
    const caller = appRouter.createCaller(ctx);
    
    const result = await caller.strategy.backtestParams({
      shortMaPeriod: 5,
      longMaPeriod: 20,
      timeframe: "1h",
      sensitivity: "standard",
    });
    
    expect(result.totalTrades).toBeGreaterThan(0);
  });
});
```

## 运行测试

### 本地开发

```bash
# 运行单元测试（快速，默认）
pnpm test

# 运行集成测试（需要完整环境）
pnpm test:integration

# 运行所有测试
pnpm test:all
```

### CI/CD环境

GitHub Actions只运行单元测试：

```yaml
# .github/workflows/deploy.yml
- name: Run tests
  run: pnpm test  # 只运行单元测试
  continue-on-error: false
```

**原因：**
- CI环境没有Python脚本和依赖
- CI环境没有数据库连接
- 集成测试执行时间长，影响部署速度

## 测试配置

### vitest.config.ts（单元测试）

```typescript
export default defineConfig({
  test: {
    include: ["server/**/*.test.ts"],
    exclude: [
      "node_modules",
      "server/**/*.integration.test.ts", // 排除集成测试
    ],
    testTimeout: 30000,
  },
});
```

### vitest.integration.config.ts（集成测试）

```typescript
export default defineConfig({
  test: {
    include: ["server/**/*.integration.test.ts"], // 只包含集成测试
    testTimeout: 60000, // 更长的超时时间
  },
});
```

## 编写测试指南

### 单元测试最佳实践

1. **使用Mock数据**

```typescript
function createTestContext(): TrpcContext {
  const user: AuthenticatedUser = {
    id: 1,
    openId: "test-user",
    email: "test@example.com",
    // ... mock数据
  };
  
  return { user, req: {} as any, res: {} as any };
}
```

2. **测试业务逻辑，不测试实现细节**

```typescript
// ✅ 好：测试行为
it("should return user info when authenticated", async () => {
  const result = await caller.auth.me();
  expect(result.email).toBe("test@example.com");
});

// ❌ 坏：测试实现
it("should call getUserByOpenId function", async () => {
  const spy = vi.spyOn(db, "getUserByOpenId");
  await caller.auth.me();
  expect(spy).toHaveBeenCalled();
});
```

3. **一个测试只验证一个行为**

```typescript
// ✅ 好
it("should clear session cookie", async () => {
  await caller.auth.logout();
  expect(clearedCookies).toHaveLength(1);
});

it("should return success status", async () => {
  const result = await caller.auth.logout();
  expect(result.success).toBe(true);
});

// ❌ 坏
it("should logout correctly", async () => {
  const result = await caller.auth.logout();
  expect(result.success).toBe(true);
  expect(clearedCookies).toHaveLength(1);
  expect(clearedCookies[0].name).toBe(COOKIE_NAME);
});
```

### 集成测试最佳实践

1. **在测试前检查环境**

```typescript
describe("Python integration", () => {
  beforeAll(() => {
    if (!process.env.PYTHON_AVAILABLE) {
      throw new Error("Python environment not available");
    }
  });
  
  it("should run Python script", async () => {
    // ...
  });
});
```

2. **使用真实数据库（测试数据库）**

```typescript
beforeEach(async () => {
  // 清理测试数据
  await db.delete(testTable);
});

afterEach(async () => {
  // 清理测试数据
  await db.delete(testTable);
});
```

3. **设置合理的超时时间**

```typescript
it("should complete backtest", async () => {
  // 回测可能需要30秒
  const result = await caller.strategy.backtestParams(params);
  expect(result).toBeDefined();
}, 60000); // 60秒超时
```

## 当前测试状态

### 单元测试（24个通过）

- ✅ `auth.logout.test.ts` - 认证登出
- ✅ `emergency_stop.test.ts` - 紧急停止功能
- ✅ `strategy.params.test.ts` - 策略参数
- ✅ `dashboard.test.ts` - Dashboard API
- ✅ `v35_features.test.ts` - v35功能

### 集成测试（14个跳过）

- ⏭️ `v24.features.test.ts` - v24功能（需要Python测试模式脚本）
- ⏭️ `strategy.backtest.test.ts` - 策略回测（需要Python回测脚本）

**跳过原因：**
这些测试依赖Python脚本和完整的交易环境，在CI环境中无法运行。

## 迁移现有测试

如果某个测试需要外部依赖，应该将其重命名为 `*.integration.test.ts`：

```bash
# 重命名集成测试
mv server/v24.features.test.ts server/v24.features.integration.test.ts
mv server/strategy.backtest.test.ts server/strategy.backtest.integration.test.ts
```

然后移除 `describe.skip`，让测试正常运行（仅在本地）：

```typescript
// 之前
describe.skip("v24.0 新增功能测试", () => {
  // ...
});

// 之后（重命名为 .integration.test.ts）
describe("v24.0 新增功能测试", () => {
  // ...
});
```

## 测试覆盖率

```bash
# 生成测试覆盖率报告
pnpm test --coverage

# 查看覆盖率报告
open coverage/index.html
```

**目标：**
- 单元测试覆盖率 > 80%
- 关键业务逻辑覆盖率 > 95%

## 故障排查

### 问题1：测试超时

```typescript
// 增加超时时间
it("slow test", async () => {
  // ...
}, 60000); // 60秒

// 或在配置中全局设置
// vitest.config.ts
test: {
  testTimeout: 60000,
}
```

### 问题2：数据库连接失败

```typescript
// 检查数据库是否可用
beforeAll(async () => {
  const db = await getDb();
  if (!db) {
    throw new Error("Database not available");
  }
});
```

### 问题3：Python脚本未找到

```typescript
// 检查Python脚本是否存在
import { existsSync } from 'fs';

beforeAll(() => {
  const scriptPath = '/path/to/script.py';
  if (!existsSync(scriptPath)) {
    throw new Error(`Python script not found: ${scriptPath}`);
  }
});
```

## 相关资源

- [Vitest文档](https://vitest.dev/)
- [Testing Best Practices](https://github.com/goldbergyoni/javascript-testing-best-practices)
- [tRPC Testing](https://trpc.io/docs/server/testing)
