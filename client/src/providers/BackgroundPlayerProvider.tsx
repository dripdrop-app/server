import {
  createContext,
  ReactNode,
  RefObject,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import { skipToken } from "@reduxjs/toolkit/query";

import { GetYoutubeVideosApiYoutubeVideosListGetApiArg as YoutubeVideosParams } from "../api/generated/youtubeApi";
import { useFooter } from "./FooterProvider";
import { YoutubeVideoResponse as YoutubeVideo } from "../api/generated/youtubeApi";
import { useYoutubeVideosQuery } from "../api/youtube";
import { getYoutubePlayerApi } from "../utils/youtubePlayer";

interface BackgroundPlayerContextType {
  addVideoToQueue: ({ index, params }: { index: number; params: YoutubeVideosParams }) => void;
  advanceQueue: () => void;
  canAdvanceQueue: boolean;
  canRecedeQueue: boolean;
  currentPageVideos: YoutubeVideo[];
  currentVideo?: YoutubeVideo;
  currentVideoIndex: number;
  goToVideoIndex: (index: number) => void;
  params?: YoutubeVideosParams;
  playing: boolean;
  recedeQueue: () => void;
  setPlaying: (playing: boolean) => void;
  setShowPlayer: (show: boolean) => void;
  showPlayer: boolean;
  playerRef: RefObject<HTMLVideoElement | null>;
}

const BackgroundPlayerContext = createContext<BackgroundPlayerContextType | undefined>(undefined);

export const BackgroundPlayerProvider = ({ children }: { children: ReactNode }) => {
  const { setDisplayFooter } = useFooter();

  const [currentVideoIndex, setCurrentVideoIndex] = useState(0);
  const [params, setParams] = useState<YoutubeVideosParams>();
  const [showPlayer, setShowPlayer] = useState(false);
  const playerRef = useRef<HTMLVideoElement | null>(null);
  const [playing, setPlaying] = useState(false);

  const videosStatus = useYoutubeVideosQuery(params ?? skipToken);
  const currentPageVideos = useMemo(() => videosStatus.currentData?.videos ?? [], [videosStatus.currentData]);

  const addVideoToQueue = useCallback(({ index, params }: { index: number; params: YoutubeVideosParams }) => {
    setCurrentVideoIndex(index);
    setParams(params);
    setPlaying(true);
  }, []);

  const goToVideoIndex = useCallback((index: number) => {
    setCurrentVideoIndex(index);
  }, []);

  const currentVideo = useMemo(() => currentPageVideos[currentVideoIndex], [currentPageVideos, currentVideoIndex]);

  const canAdvanceQueue = useMemo(() => {
    if (videosStatus.currentData && params) {
      return currentVideoIndex + 1 < currentPageVideos.length || params.page + 1 <= videosStatus.currentData.totalPages;
    }
    return false;
  }, [currentPageVideos.length, currentVideoIndex, params, videosStatus.currentData]);

  // The single place that decides whether "next"/"previous" should skip within the
  // current page's YouTube playlist (via the player's own API) or roll over to an
  // adjacent page. Keeping this decision here (instead of duplicating it wherever a
  // skip button lives) is what keeps the player's index and this queue's index in sync.
  const advanceQueue = useCallback(() => {
    if (!canAdvanceQueue || !videosStatus.currentData || !params) {
      return;
    }

    if (currentVideoIndex + 1 < currentPageVideos.length) {
      const api = getYoutubePlayerApi(playerRef.current);
      if (api) {
        api.nextVideo();
      } else {
        setCurrentVideoIndex(currentVideoIndex + 1);
      }
    } else if (params.page + 1 <= videosStatus.currentData.totalPages) {
      setParams({ ...params, page: params.page + 1 });
      setCurrentVideoIndex(0);
    }

    // Restore playback after advancing. react-player fires onPause before onEnded
    // when a video finishes, which clears playing before we load the next track.
    setPlaying(true);
  }, [canAdvanceQueue, currentPageVideos.length, currentVideoIndex, params, videosStatus.currentData]);

  const canRecedeQueue = useMemo(() => {
    if (params) {
      return currentVideoIndex > 0 || params.page > 1;
    }
    return false;
  }, [currentVideoIndex, params]);

  const recedeQueue = useCallback(() => {
    if (!canRecedeQueue || !videosStatus.currentData || !params) {
      return;
    }

    if (currentVideoIndex > 0) {
      const api = getYoutubePlayerApi(playerRef.current);
      if (api) {
        api.previousVideo();
      } else {
        setCurrentVideoIndex(currentVideoIndex - 1);
      }
    } else if (params.page > 1) {
      setParams({ ...params, page: params.page - 1 });
      setCurrentVideoIndex(params.perPage - 1);
    }
  }, [canRecedeQueue, currentVideoIndex, params, videosStatus.currentData]);

  useEffect(() => {
    setDisplayFooter(showPlayer);
  }, [setDisplayFooter, showPlayer]);

  return (
    <BackgroundPlayerContext.Provider
      value={{
        addVideoToQueue,
        advanceQueue,
        canAdvanceQueue,
        canRecedeQueue,
        currentPageVideos,
        currentVideo,
        currentVideoIndex,
        goToVideoIndex,
        params,
        playing,
        playerRef,
        recedeQueue,
        setPlaying,
        setShowPlayer,
        showPlayer,
      }}
    >
      {children}
    </BackgroundPlayerContext.Provider>
  );
};

export const useBackgroundPlayer = () => {
  const context = useContext(BackgroundPlayerContext);

  if (context === undefined) {
    throw new Error("useBackgroundPlayer must be used within a BackgroundPlayerProvider");
  }
  return context;
};
