/**
 * Pyodide FS에 파일을 “사전로딩(preload)” 합니다.
 *
 * @param {Object} pyodide            — loadPyodide()로 얻은 인스턴스
 * @param {Array<{url: string, path: string}>} assets
 *        — url: 브라우저가 fetch할 리소스 경로
 *        — path: Pyodide FS 안에 생성될 파일 경로 (예: "sounds/boom.wav")
 */
async function preloadAssets(pyodide, assets) {
  const FS = pyodide.FS;
    console.log(FS)
  await Promise.all(assets.map(({ url, path }) => {
    return new Promise((resolve, reject) => {
      // 1) 디렉터리 구조 만들기
      const parts = path.split('/');
      const filename = parts.pop();
      const dir = parts.length ? parts.join('/') : '/';
      if (dir !== '/' && !FS.analyzePath(dir).exists) {
        FS.mkdirTree(dir);
      }

      // 2) Emscripten에 내장된 비동기 프리로드 함수 호출
      //    onload / onerror 콜백을 통해 완료 시점 보장
      FS.createPreloadedFile(
        dir,              // parent folder in virtual FS
        filename,         // file name
        url,              // HTTP URL to fetch
        /* canRead */  true,
        /* canWrite */ true,
        () => resolve(),  // onload
        (err) => reject(  // onerror
          new Error(`FS.createPreloadedFile error: ${url}\n${err}`)
        ),
        /* dontCreateFile */ false
      );
    });
  }));
}
/**
 * 디버깅용 함수입니다.
 * Pyodide 가상 파일시스템 전체를 트리 형태로 출력합니다.
 *
 * @param {Object} pyodide      — loadPyodide()로 얻은 인스턴스
 * @param {string} [startPath]  — 순회를 시작할 경로 (기본 "/")
 */
function printVFS(pyodide, startPath = "/") {
  const FS = pyodide.FS;

  /**
   * @param {string} path  — 현재 디렉터리 경로
   * @param {number} depth — 들여쓰기 레벨
   */
  function walk(path, depth) {
    const indent = "  ".repeat(depth);
    // "."와 ".."는 제외
    const entries = FS.readdir(path).filter(name => name !== "." && name !== "..");
    for (const name of entries) {
      const fullPath = path === "/" ? `/${name}` : `${path}/${name}`;
      let stat;
      try {
        stat = FS.stat(fullPath);
      } catch (err) {
        console.warn(`⚠️ stat 에러: ${fullPath}`, err);
        continue;
      }
      const isDir = FS.isDir(stat.mode);
      console.log(`${indent}${isDir ? "📁" : "📄"} ${name}`);
      if (isDir) {
        walk(fullPath, depth + 1);
      }
    }
  }

  console.group(`Pyodide VFS: "${startPath}"`);
  walk(startPath, 0);
  console.groupEnd();
}
