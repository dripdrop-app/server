import React, { forwardRef, useCallback, useEffect, useMemo, useRef } from "react";
import ReactPlayer from "react-player";

import { YoutubeVideoResponse as YoutubeVideo } from "../../api/generated/youtubeApi";
import { useAddYoutubeVideoWatchMutation } from "../../api/youtube";
import { buildYoutubePlaylistConfig, buildYoutubeWatchUrl, getYoutubePlayerApi } from "../../utils/youtubePlayer";

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
    const lastPlaylistIndexRef = useRef(playlistIndex);
    const activeVideoRef = useRef<YoutubeVideo | null | undefined>(video);

    const playlistVideos = useMemo(() => playlist ?? (video ? [video] : []), [playlist, video]);
    const playlistIds = useMemo(() => playlistVideos.map((playlistVideo) => playlistVideo.id), [playlistVideos]);
    const usePlaylist = playlistIds.length > 1;

    const src = useMemo(() => {
      if (!playlistIds.length) {
        return undefined;
      }

      const startIndex = usePlaylist ? 0 : Math.min(playlistIndex, playlistIds.length - 1);
      return buildYoutubeWatchUrl(playlistIds[startIndex]);
    }, [playlistIds, playlistIndex, usePlaylist]);

    const config = useMemo(() => buildYoutubePlaylistConfig(playlistIds), [playlistIds]);

    const resolveActiveVideo = useCallback(
      (player: HTMLVideoElement | null) => {
        if (!playlistVideos.length) {
          activeVideoRef.current = video;
          return video;
        }

        const api = getYoutubePlayerApi(player);
        const videoId = api?.getVideoData()?.video_id;
        const index = api?.getPlaylistIndex();

        if (videoId) {
          const matchedVideo = playlistVideos.find((playlistVideo) => playlistVideo.id === videoId);
          if (matchedVideo) {
            activeVideoRef.current = matchedVideo;
            return matchedVideo;
          }
        }

        if (index != null && playlistVideos[index]) {
          activeVideoRef.current = playlistVideos[index];
          return playlistVideos[index];
        }

        activeVideoRef.current = video;
        return video;
      },
      [playlistVideos, video]
    );

    const syncPlaylistIndex = useCallback(
      (player: HTMLVideoElement | null) => {
        const api = getYoutubePlayerApi(player);
        if (!api || !usePlaylist) {
          return;
        }

        const index = api.getPlaylistIndex();
        if (index === lastPlaylistIndexRef.current) {
          return;
        }

        lastPlaylistIndexRef.current = index;
        onActiveVideoChange?.(index);
        resolveActiveVideo(player);
      },
      [onActiveVideoChange, resolveActiveVideo, usePlaylist]
    );

    const seekToPlaylistIndex = useCallback(
      (player: HTMLVideoElement | null, index: number) => {
        const api = getYoutubePlayerApi(player);
        if (!api || !usePlaylist || index === api.getPlaylistIndex()) {
          return;
        }

        api.playVideoAt(index);
        lastPlaylistIndexRef.current = index;
      },
      [usePlaylist]
    );

    useEffect(() => {
      activeVideoRef.current = video;
      lastPlaylistIndexRef.current = playlistIndex;
    }, [video?.id, playlistIndex]);

    useEffect(() => {
      const player = typeof ref === "function" ? null : ref?.current;
      if (!player || !usePlaylist) {
        return;
      }

      seekToPlaylistIndex(player, playlistIndex);
    }, [playlistIndex, ref, seekToPlaylistIndex, usePlaylist]);

    const handleReady = useCallback(() => {
      const player = typeof ref === "function" ? null : ref?.current;
      if (player) {
        seekToPlaylistIndex(player, playlistIndex);
        resolveActiveVideo(player);
      }

      onReady?.();
    }, [onReady, playlistIndex, ref, resolveActiveVideo, seekToPlaylistIndex]);

    const handlePlaying = useCallback(() => {
      const player = typeof ref === "function" ? null : ref?.current;
      if (player) {
        syncPlaylistIndex(player);
        resolveActiveVideo(player);
      }
    }, [ref, resolveActiveVideo, syncPlaylistIndex]);

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
          onReady={handleReady}
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
            const api = getYoutubePlayerApi(event.currentTarget);
            const index = api?.getPlaylistIndex() ?? playlistIndex;

            if (!usePlaylist || index >= playlistIds.length - 1) {
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
        onDuration,
        onEnd,
        onPause,
        onPlay,
        onProgress,
        playlistIds,
        playlistIndex,
        playing,
        ref,
        resolveActiveVideo,
        src,
        style,
        usePlaylist,
        watchVideo,
        width,
      ]
    );
  }
);

export default VideoPlayer;
