// N-04: 地理院タイル・CC BY データの帰属を常時表示
export default function Attribution() {
  return (
    <footer className="attribution">
      地図タイル:{" "}
      <a href="https://maps.gsi.go.jp/development/ichiran.html" target="_blank" rel="noreferrer">
        国土地理院
      </a>
      {" ｜ データ: "}
      <a href="https://catalog.data.metro.tokyo.lg.jp/" target="_blank" rel="noreferrer">
        東京都オープンデータ
      </a>
      (CC BY 4.0)・
      <a href="https://www.wikidata.org/" target="_blank" rel="noreferrer">
        Wikidata
      </a>
      (CC0)・自前調査(CC BY 4.0)
      {" ｜ コード: "}
      <a
        href="https://github.com/twill3c/tsukiji-atlas/blob/main/LICENSE"
        target="_blank"
        rel="noreferrer"
      >
        MIT License
      </a>
      {" © 2026 坂田哲朗 ・ "}
      <a href="https://github.com/twill3c/tsukiji-atlas" target="_blank" rel="noreferrer">
        GitHub
      </a>
      {" ・ "}
      <a
        href="https://claude.ai/code/artifact/1bc21b09-1ae9-4099-88c8-d867ad78965c"
        target="_blank"
        rel="noreferrer"
      >
        築地アトラスの歩き方
      </a>
      {" ・ "}
      <a
        href="https://claude.ai/code/artifact/41b74928-fb07-481d-a038-51397f28880f"
        target="_blank"
        rel="noreferrer"
      >
        築地アトラス設計図
      </a>
      {" ・ "}
      <a href="https://app-menu-amber.vercel.app" target="_blank" rel="noopener">
        App Menu
      </a>
    </footer>
  );
}
