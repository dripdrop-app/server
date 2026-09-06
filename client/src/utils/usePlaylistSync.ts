import { ForwardedRef, useCallback, useEffect, useMemo, useRef } from "react";

import { YoutubeVideoResponse as YoutubeVideo } from "../api/generated/youtubeApi";
import { buildYoutubePlaylistConfig, buildYoutubeWatchUrl, getYoutubePlayerApi } from "./youtubePlayer";

interface UsePlaylistSyncArgs {
  ref: ForwardedRef<HTMLVideoElement>;
  video: YoutubeVideo | null | undefined;
  playlist?: YoutubeVideo[];
  playlistIndex: number;
  onActiveVideoChange?: (index: number) => void;
}

const getPlayerFromRef = (ref: ForwardedRef<HTMLVideoElement>) =>
  typeof ref === "function" ? null : (ref?.current ?? null);

// Bridges the YouTube player's own imperative playlist position with the
// `playlistIndex` prop that drives it from React. The two never fully merge into a
// single source of truth: the player can move on its own (native prev/next controls,
// the playlist auto-advancing), and the parent can move it externally (picking a video
// from "Up Next"), so this hook has to both push prop changes into the player and pull
// player-driven changes back out.
const usePlaylistSync = ({ ref, video, playlist, playlistIndex, onActiveVideoChange }: UsePlaylistSyncArgs) => {
  const lastPlaylistIndexRef = useRef(playlistIndex);

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

  // Reads the player's own playlist position fresh on every call (rather than caching
  // it in a ref that's read elsewhere) because a ref mutation alone doesn't trigger a
  // re-render, so a cached value read from render-time state could go stale between
  // ticks of onTimeUpdate, which fires many times per second.
  const resolveActiveVideo = useCallback(
    (player: HTMLVideoElement | null) => {
      if (!playlistVideos.length) {
        return video;
      }

      const index = getYoutubePlayerApi(player)?.getPlaylistIndex();
      return (index != null && playlistVideos[index]) || video;
    },
    [playlistVideos, video]
  );

  // Pull: notice when the player's playlist index has moved on its own and report it
  // upward, so the parent's notion of "current index" stays in sync.
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
    },
    [onActiveVideoChange, usePlaylist]
  );

  // Push: drive the player to a specific index requested from outside.
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
    lastPlaylistIndexRef.current = playlistIndex;
  }, [video?.id, playlistIndex]);

  // Handles playlistIndex changing while the player is already mounted and ready.
  useEffect(() => {
    const player = getPlayerFromRef(ref);
    if (!player || !usePlaylist) {
      return;
    }

    seekToPlaylistIndex(player, playlistIndex);
  }, [playlistIndex, ref, seekToPlaylistIndex, usePlaylist]);

  // Handles the initial seek once the player becomes ready. This has to stay separate
  // from the effect above: the player element remounts on every page change (see the
  // `key` on ReactPlayer), firing a fresh "ready" event each time, but that doesn't by
  // itself change any dependency the effect above would re-run for.
  const handleReady = useCallback(() => {
    const player = getPlayerFromRef(ref);
    if (player) {
      seekToPlaylistIndex(player, playlistIndex);
    }
  }, [playlistIndex, ref, seekToPlaylistIndex]);

  const handlePlaying = useCallback(() => {
    syncPlaylistIndex(getPlayerFromRef(ref));
  }, [ref, syncPlaylistIndex]);

  const isPlaylistFinished = useCallback(
    (player: HTMLVideoElement | null) => {
      const index = getYoutubePlayerApi(player)?.getPlaylistIndex() ?? playlistIndex;
      return !usePlaylist || index >= playlistIds.length - 1;
    },
    [playlistIds.length, playlistIndex, usePlaylist]
  );

  return { playlistIds, src, config, resolveActiveVideo, handleReady, handlePlaying, isPlaylistFinished };
};

export default usePlaylistSync;
