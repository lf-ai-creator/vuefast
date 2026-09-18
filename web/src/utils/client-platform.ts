interface PlatformHints {
  platform?: string;
  platformVersion?: string;
}

type NavigatorWithHints = Navigator & {
  userAgentData?: {
    getHighEntropyValues: (hints: string[]) => Promise<PlatformHints>;
  };
};

let platformHints: Promise<PlatformHints> | undefined;

export async function getClientPlatform(): Promise<PlatformHints> {
  const agent = (navigator as NavigatorWithHints).userAgentData;
  if (!agent) return {};
  platformHints ??= Promise.resolve()
    .then(() => agent.getHighEntropyValues(["platform", "platformVersion"]))
    .catch(() => ({}));
  let timeout: ReturnType<typeof setTimeout> | undefined;
  try {
    return await Promise.race([
      platformHints,
      new Promise<PlatformHints>((resolve) => {
        timeout = setTimeout(() => resolve({}), 500);
      }),
    ]);
  } finally {
    clearTimeout(timeout);
  }
}
