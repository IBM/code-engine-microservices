async function fetcher(url) {
  return await fetch(url, {
    headers: {
      "Access-Control-Allow-Headers": "X-INSTANA-T, X-INSTANA-S, X-INSTANA-L"
    }
  }).then((res) => {
    if (!res.ok) {
      throw Error(res.statusText);
    }
    return res.json();
  });
}

export async function fetcher2(_urls) {
  const urls = JSON.parse(_urls);
  const fetches = urls.map(async (url) => {
    return await fetch(url, {
      headers: {
        "Access-Control-Allow-Headers": "X-INSTANA-T, X-INSTANA-S, X-INSTANA-L"
      }
    }).then((res) => {
      if (!res.ok) {
        throw Error(res.statusText);
      }
      return res.json();
    });
  });
  return await Promise.all(fetches);
}

export default fetcher;
