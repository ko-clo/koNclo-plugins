#!/usr/bin/env node
// 데스크톱 확장(.mcpb) 빌드 — `npm run build` 가 이 파일을 부른다.
//
// mcpb pack 은 출력 파일 경로를 반드시 받아야 하고(디렉터리를 주면 EISDIR),
// 파일 이름에 버전을 직접 적으면 manifest 와 어긋난다. 그래서 여기서
// manifest.json 의 version 을 읽어 이름을 만든다.
import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, readdirSync, existsSync } from "node:fs";
import { join } from "node:path";

// 빌드 도구는 버전을 고정한다 — 같은 소스가 언제 빌드해도 같은 결과여야 한다.
const MCPB_PACKAGE = "@anthropic-ai/mcpb@2.1.2";
const PLUGINS_DIR = "plugins";
const OUTPUT_DIR = "dist";

/** manifest.json 을 가진 플러그인만 데스크톱 확장으로 포장할 수 있다. */
function findBundlablePlugins() {
  if (!existsSync(PLUGINS_DIR)) return [];
  return readdirSync(PLUGINS_DIR, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => join(PLUGINS_DIR, entry.name))
    .filter((dir) => existsSync(join(dir, "manifest.json")));
}

function readManifest(pluginDir) {
  return JSON.parse(readFileSync(join(pluginDir, "manifest.json"), "utf8"));
}

function run(args) {
  execFileSync("npx", ["-y", MCPB_PACKAGE, ...args], { stdio: "inherit" });
}

function main() {
  const requested = process.argv[2];
  let plugins = findBundlablePlugins();

  if (requested) {
    plugins = plugins.filter((dir) => dir.endsWith(`/${requested}`));
    if (plugins.length === 0) {
      console.error(`manifest.json 을 가진 '${requested}' 플러그인을 찾지 못했습니다.`);
      process.exit(1);
    }
  }

  if (plugins.length === 0) {
    console.error(`${PLUGINS_DIR}/ 아래에 manifest.json 을 가진 플러그인이 없습니다.`);
    process.exit(1);
  }

  mkdirSync(OUTPUT_DIR, { recursive: true });

  for (const pluginDir of plugins) {
    const { name, version } = readManifest(pluginDir);
    const outputPath = join(OUTPUT_DIR, `${name}-${version}.mcpb`);

    console.log(`\n▶ ${name} ${version} 검증`);
    run(["validate", join(pluginDir, "manifest.json")]);

    console.log(`▶ ${name} ${version} 패킹 → ${outputPath}`);
    run(["pack", pluginDir, outputPath]);
  }

  console.log(`\n완료 — ${OUTPUT_DIR}/ 에 ${plugins.length}개 번들을 만들었습니다.`);
}

main();
