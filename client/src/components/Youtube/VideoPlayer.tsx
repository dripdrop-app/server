import React, { forwardRef, useMemo } from "react";
import ReactPlayer from "react-player";

import { YoutubeVideoResponse as YoutubeVideo } from "../../api/generated/youtubeApi";
import { useAddYoutubeVideoWatchMutation } from "../../api/youtube";
import usePlaylistSync from "../../utils/usePlaylistSync";

export interface ProgressState {
  playedSeconds: number;
}

interface VideoPlayerProps {
  video: YoutubeVideo | null | undefined;
  playlist?: YoutubeVideo[];
  playlistIndex?: number;
  playing?: boolean;
  onDuration?: (duration: number) => void;
  onEnd?: () => void;
  onReady?: () => void;
  onProgress?: (state: ProgressState) => void;
  onPlay?: () => void;
  onPause?: () => void;
  onActiveVideoChange?: (index: number) => void;
  width?: string;
  height?: string;
  style?: React.CSSProperties;
}

const VideoPlayer = forwardRef<HTMLVideoElement, VideoPlayerProps>(
  (
    {
      video,
      playlist,
      playlistIndex = 0,
      onDuration,
      onProgress,
      onEnd,
      onReady,
      onPlay,
      onPause,
      onActiveVideoChange,
      playing,
      height,
      width,
      style,
    },
    ref
  ) => {
    const [watchVideo] = useAddYoutubeVideoWatchMutation();

    const { playlistIds, src, config, resolveActiveVideo, handleReady, handlePlaying, isPlaylistFinished } =
      usePlaylistSync({ ref, video, playlist, playlistIndex, onActiveVideoChange });

    return useMemo(
      () => (
        <ReactPlayer
          key={playlistIds.join(",")}
          ref={ref}
          style={style}
          height={height || "100%"}
          width={width || "100%"}
          playing={playing}
          controls={true}
          src={src}
          config={config}
          onPlay={() => {
            onPlay?.();
            handlePlaying();
          }}
          onPause={() => {
            onPause?.();
          }}
          onReady={() => {
            handleReady();
            onReady?.();
          }}
          onPlaying={handlePlaying}
          onDurationChange={(event) => {
            const duration = event.currentTarget.duration;
            if (onDuration && Number.isFinite(duration)) {
              onDuration(duration);
            }
          }}
          onTimeUpdate={(event) => {
            const playedSeconds = event.currentTarget.currentTime;
            const activeVideo = resolveActiveVideo(event.currentTarget);

            if (activeVideo) {
              onProgress?.({ playedSeconds });

              if (playedSeconds > 20 && !activeVideo.watched) {
                watchVideo(activeVideo.id);
              }
            }
          }}
          onEnded={(event) => {
            if (isPlaylistFinished(event.currentTarget)) {
              onEnd?.();
            }
          }}
        />
      ),
      [
        config,
        handlePlaying,
        handleReady,
        height,
        isPlaylistFinished,
        onDuration,
        onEnd,
        onPause,
        onPlay,
        onProgress,
        onReady,
        playlistIds,
        playing,
        ref,
        resolveActiveVideo,
        src,
        style,
        watchVideo,
        width,
      ]
    );
  }
);

export default VideoPlayer;
