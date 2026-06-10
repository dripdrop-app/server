export interface YoutubePlayerApi {
  getPlaylistIndex: () => number;
  getVideoData: () => { video_id: string };
  nextVideo: () => void;
  previousVideo: () => void;
  playVideoAt: (index: number) => void;
}

interface YoutubePlayerElement extends HTMLVideoElement {
  api?: YoutubePlayerApi;
}

export const getYoutubePlayerApi = (player: HTMLVideoElement | null): YoutubePlayerApi | undefined =>
  (player as YoutubePlayerElement | null)?.api;

export const buildYoutubeWatchUrl = (videoId: string) => `https://www.youtube.com/watch?v=${videoId}`;

export const buildYoutubePlaylistConfig = (videoIds: string[]) => {
  if (videoIds.length <= 1) {
    return undefined;
  }

  return {
    youtube: {
      playlist: videoIds.slice(1).join(","),
    },
  };
};
