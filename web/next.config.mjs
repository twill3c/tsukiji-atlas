/** 静的エクスポート(F-08)。サーバ・環境変数不要で Vercel/任意の静的ホストに置ける */
const nextConfig = {
  output: "export",
  images: { unoptimized: true },
};

export default nextConfig;
