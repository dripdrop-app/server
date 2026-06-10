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

interface BackgroundPlayerContextType {
  addVideoToQueue: ({ index, params }: { index: number; params: YoutubeVideosParams }) => void;
  advanceQueue: () => void;
  canAdvanceQueue: boolean;
  canRecedeQueue: boolean;
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

  const addVideoToQueue = useCallback(({ index, params }: { index: number; params: YoutubeVideosParams }) => {
    setCurrentVideoIndex(index);
    setParams(params);
    setPlaying(true);
  }, []);

  const goToVideoIndex = useCallback((index: number) => {
    setCurrentVideoIndex(index);
  }, []);

  const currentVideo = useMemo(
    () => videosStatus.currentData?.videos[currentVideoIndex],
    [currentVideoIndex, videosStatus.currentData?.videos]
  );

  const canAdvanceQueue = useMemo(() => {
    if (videosStatus.currentData && params) {
      return (
        currentVideoIndex + 1 < videosStatus.currentData?.videos.length ||
        params.page + 1 <= videosStatus.currentData.totalPages
      );
    }
    return false;
  }, [currentVideoIndex, params, videosStatus.currentData]);

  const advanceQueue = useCallback(() => {
    if (canAdvanceQueue && videosStatus.currentData && params) {
      if (currentVideoIndex + 1 < videosStatus.currentData?.videos.length) {
        setCurrentVideoIndex(currentVideoIndex + 1);
      } else if (params.page <= videosStatus.currentData.totalPages) {
        setParams({ ...params, page: params.page + 1 });
        setCurrentVideoIndex(0);
      }
      // Restore playback after advancing. react-player fires onPause before onEnded
      // when a video finishes, which clears playing before we load the next track.
      setPlaying(true);
    }
  }, [canAdvanceQueue, currentVideoIndex, params, videosStatus.currentData]);

  const canRecedeQueue = useMemo(() => {
    if (params) {
      return currentVideoIndex > 0 || params.page > 1;
    }
    return false;
  }, [currentVideoIndex, params]);

  const recedeQueue = useCallback(() => {
    if (canRecedeQueue && videosStatus.currentData && params) {
      if (currentVideoIndex > 0) {
        setCurrentVideoIndex(currentVideoIndex - 1);
      } else if (params.page > 1) {
        setParams({ ...params, page: params.page - 1 });
        setCurrentVideoIndex(params.perPage - 1);
      }
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
