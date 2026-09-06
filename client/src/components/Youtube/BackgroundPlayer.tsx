import {
  ActionIcon,
  Avatar,
  Box,
  Card,
  Center,
  CloseButton,
  Divider,
  Grid,
  Group,
  List,
  Overlay,
  Pagination,
  ScrollArea,
  Slider,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import { useCallback, useEffect, useRef, useState } from "react";
import { CgPlayTrackNext, CgPlayTrackPrev } from "react-icons/cg";
import { FaAngleUp, FaPause, FaPlay } from "react-icons/fa";

import { useClickOutside, useDisclosure } from "@mantine/hooks";
import { Link } from "react-router-dom";
import { VideoLikeButton, VideoQueueButton } from "./VideoButtons";
import VideoPlayer from "./VideoPlayer";
import { createPortal } from "react-dom";
import { useFooter } from "../../providers/FooterProvider";
import { useOverlay } from "../../providers/OverlayProvider";
import { useBackgroundPlayer } from "../../providers/BackgroundPlayerProvider";
import { MdClose } from "react-icons/md";
import { useYoutubeVideosQuery } from "../../api/youtube";
import { skipToken } from "@reduxjs/toolkit/query";

const BackgroundPlayer = () => {
  const {
    addVideoToQueue,
    currentVideo,
    advanceQueue,
    params,
    playing,
    playerRef,
    recedeQueue,
    setPlaying,
    setShowPlayer,
  } = useBackgroundPlayer();

  const [queueParams, setQueueParams] = useState(params);
  const videosStatus = useYoutubeVideosQuery(queueParams ?? skipToken);

  const [duration, setDuration] = useState(0);
  const [playedSeconds, setPlayedSeconds] = useState(0);
  const [seekValue, setSeekValue] = useState(0);
  const [isSeeking, setIsSeeking] = useState(false);
  const seekingRef = useRef(false);
  const playedSecondsRef = useRef(0);

  const sliderValue = duration > 0 ? (isSeeking ? seekValue : (playedSeconds / duration) * 100) : 0;
  const displayedSeconds = isSeeking ? (seekValue / 100) * duration : playedSeconds;

  const [expand, { toggle: toggleExpand }] = useDisclosure(false);
  const { footerRef } = useFooter();
  const { overlayRef } = useOverlay();
  const clickOutsideRef = useClickOutside(() => {
    if (expand) toggleExpand();
  });

  const channelLink = `/youtube/channel/${currentVideo?.channel.id}`;
  const videoLink = `/youtube/video/${currentVideo?.id}`;

  const convertToTimeString = (seconds: number) => {
    seconds = Math.round(seconds);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds < 10 ? `0${remainingSeconds}` : remainingSeconds}`;
  };

  useEffect(() => {
    seekingRef.current = false;
    setIsSeeking(false);
    setDuration(0);
    setPlayedSeconds(0);
    setSeekValue(0);
  }, [currentVideo?.id]);

  const handleDuration = useCallback((nextDuration: number) => {
    setDuration(nextDuration);
  }, []);

  const handleProgress = useCallback((playedSeconds: number) => {
    if (seekingRef.current) {
      return;
    }
    setPlayedSeconds(playedSeconds);
  }, []);

  const handleSeekChange = useCallback(
    (value: number) => {
      seekingRef.current = true;
      setIsSeeking(true);
      setSeekValue(value);

      const player = playerRef.current;
      if (player && Number.isFinite(player.duration)) {
        player.currentTime = (value / 100) * player.duration;
      }
    },
    [playerRef]
  );

  const handleSeekChangeEnd = useCallback(
    (value: number) => {
      seekingRef.current = false;
      setIsSeeking(false);

      const player = playerRef.current;
      if (player && Number.isFinite(player.duration)) {
        const seconds = (value / 100) * player.duration;
        player.currentTime = seconds;
        setPlayedSeconds(seconds);
      }
      setSeekValue(value);
    },
    [playerRef]
  );

  useEffect(() => {
    setQueueParams(params);
  }, [params]);

  useEffect(() => {
    playedSecondsRef.current = playedSeconds;
  }, [playedSeconds]);

  // Lock-screen/notification media controls, and keeps mobile browsers
  // treating this tab as an active media session so audio can continue
  // playing while the PWA is backgrounded.
  useEffect(() => {
    if (!currentVideo || !("mediaSession" in navigator)) {
      return;
    }

    navigator.mediaSession.metadata = new MediaMetadata({
      title: currentVideo.title,
      artist: currentVideo.channel.title,
      artwork: currentVideo.thumbnail ? [{ src: currentVideo.thumbnail }] : undefined,
    });
  }, [currentVideo]);

  useEffect(() => {
    if (!("mediaSession" in navigator)) {
      return;
    }
    navigator.mediaSession.playbackState = playing ? "playing" : "paused";
  }, [playing]);

  useEffect(() => {
    if (!("mediaSession" in navigator) || !navigator.mediaSession.setPositionState) {
      return;
    }
    if (!Number.isFinite(duration) || duration <= 0) {
      return;
    }
    try {
      navigator.mediaSession.setPositionState({
        duration,
        playbackRate: 1,
        position: Math.min(playedSeconds, duration),
      });
    } catch {
      // Can throw transiently if position/duration briefly disagree during a seek.
    }
  }, [duration, playedSeconds]);

  useEffect(() => {
    if (!("mediaSession" in navigator)) {
      return;
    }

    navigator.mediaSession.setActionHandler("play", () => setPlaying(true));
    navigator.mediaSession.setActionHandler("pause", () => setPlaying(false));
    navigator.mediaSession.setActionHandler("previoustrack", () => {
      if (playedSecondsRef.current < 5) {
        recedeQueue();
      } else if (playerRef.current) {
        playerRef.current.currentTime = 0;
        setPlayedSeconds(0);
        setSeekValue(0);
      }
    });
    navigator.mediaSession.setActionHandler("nexttrack", () => advanceQueue());
    navigator.mediaSession.setActionHandler("seekto", (details) => {
      if (details.seekTime === undefined) {
        return;
      }
      const player = playerRef.current;
      if (player) {
        player.currentTime = details.seekTime;
      }
      setPlayedSeconds(details.seekTime);
    });

    return () => {
      navigator.mediaSession.setActionHandler("play", null);
      navigator.mediaSession.setActionHandler("pause", null);
      navigator.mediaSession.setActionHandler("previoustrack", null);
      navigator.mediaSession.setActionHandler("nexttrack", null);
      navigator.mediaSession.setActionHandler("seekto", null);
    };
  }, [advanceQueue, playerRef, recedeQueue, setPlaying]);

  if (!footerRef.current || !overlayRef.current) {
    return null;
  }

  const VideoPlayerOverlayPortal = createPortal(
    <Overlay component={Box} display={expand ? "block" : "none"} fixed>
      <Card
        ref={clickOutsideRef}
        pos="absolute"
        top="5vh"
        right="10vw"
        w="80vw"
        padding="md"
        withBorder
        radius="md"
        shadow="md"
        display="flex"
      >
        <Card.Section inheritPadding py="xs">
          <Group justify="space-between" wrap="nowrap">
            <Group wrap="nowrap" style={{ overflowX: "hidden" }}>
              <Avatar size="md" src={currentVideo?.channel.thumbnail} style={{ borderRadius: 10 }} />
              <Text truncate="end">{currentVideo?.title}</Text>
            </Group>
            <CloseButton onClick={toggleExpand} />
          </Group>
        </Card.Section>
        <Card.Section h="80vh">
          <Grid p="sm">
            <Grid.Col h={{ xs: "40vh", md: "80vh" }} span={{ xs: 12, md: 8 }}>
              <VideoPlayer
                ref={playerRef}
                video={currentVideo}
                playing={playing}
                onPlay={() => setPlaying(true)}
                onPause={() => setPlaying(false)}
                onDuration={handleDuration}
                onProgress={(state) => handleProgress(state.playedSeconds)}
                onEnd={() => advanceQueue()}
              />
            </Grid.Col>
            <Grid.Col h={{ xs: "40vh", md: "80vh" }} span={{ xs: 12, md: 4 }}>
              <Title p="sm" order={3}>
                Up Next
              </Title>
              <ScrollArea h="90%">
                <List spacing="md" withPadding styles={{ itemWrapper: { width: "100%" } }}>
                  {videosStatus.currentData?.videos.map((v, i) => (
                    <>
                      {i > 0 && <Divider my="sm" />}
                      <List.Item
                        icon={
                          <Avatar src={v.channel.thumbnail} className={currentVideo?.id === v.id ? "rotate" : ""} />
                        }
                        className="hover-brighten"
                        style={{ cursor: "pointer" }}
                        onClick={() => {
                          if (queueParams) {
                            addVideoToQueue({
                              index: i,
                              params: queueParams,
                            });
                          }
                        }}
                      >
                        <Text>{v.title}</Text>
                        <Text c="dimmed">{v.channel.title}</Text>
                      </List.Item>
                    </>
                  ))}
                </List>
              </ScrollArea>
              <Center>
                <Pagination
                  p="sm"
                  size="sm"
                  total={videosStatus.currentData?.totalPages || 0}
                  value={queueParams?.page || 0}
                  onChange={(newPage) => {
                    if (queueParams) {
                      setQueueParams({ ...queueParams, page: newPage });
                    }
                  }}
                />
              </Center>
            </Grid.Col>
          </Grid>
        </Card.Section>
      </Card>
    </Overlay>,
    overlayRef.current
  );

  return createPortal(
    <Stack align="center" w="100%" gap={7} pos="relative">
      <Slider
        w={{ base: "90%", md: "95%" }}
        py="lg"
        step={0.1}
        min={0}
        max={100}
        marks={[
          { value: 0, label: "0:00" },
          { value: 100, label: convertToTimeString(duration) },
        ]}
        label={convertToTimeString(displayedSeconds)}
        labelAlwaysOn={true}
        value={sliderValue}
        onChange={handleSeekChange}
        onChangeEnd={handleSeekChangeEnd}
      />
      {VideoPlayerOverlayPortal}
      <Group w={{ base: "90%", md: "95%" }} gap="xl" justify="center" wrap="nowrap" style={{ overflowX: "hidden" }}>
        <Group wrap="nowrap" style={{ overflowX: "hidden" }}>
          <Avatar size="md" src={currentVideo?.thumbnail} style={{ borderRadius: 10 }} />
          <Stack gap={0} style={{ overflowX: "hidden" }}>
            <Text
              component={Link}
              className="hover-underline"
              style={{
                fontSize: "0.9em",
              }}
              truncate="end"
              to={videoLink}
            >
              {currentVideo?.title}
            </Text>
            <Text
              component={Link}
              className="hover-underline"
              style={{
                fontSize: "0.75em",
              }}
              truncate="end"
              to={channelLink}
            >
              {currentVideo?.channel.title}
            </Text>
          </Stack>
        </Group>
        <Group wrap="nowrap" visibleFrom="sm">
          {currentVideo && <VideoLikeButton video={currentVideo} />}
          {currentVideo && <VideoQueueButton video={currentVideo} />}
        </Group>
        <Group wrap="nowrap">
          <ActionIcon
            className="hover-darken"
            variant="transparent"
            onClick={() => {
              if (playedSeconds < 5) {
                recedeQueue();
              } else {
                if (playerRef.current) {
                  playerRef.current.currentTime = 0;
                }
                setPlayedSeconds(0);
                setSeekValue(0);
              }
            }}
          >
            <CgPlayTrackPrev size={25} />
          </ActionIcon>
          <ActionIcon className="hover-darken" variant="transparent" onClick={() => setPlaying(!playing)}>
            {playing ? <FaPause /> : <FaPlay />}
          </ActionIcon>
          <ActionIcon className="hover-darken" variant="transparent" onClick={advanceQueue}>
            <CgPlayTrackNext size={25} />
          </ActionIcon>
          <ActionIcon className="hover-darken" variant="transparent" onClick={toggleExpand}>
            <FaAngleUp />
          </ActionIcon>
          <ActionIcon className="hover-darken" variant="transparent" onClick={() => setShowPlayer(false)}>
            <MdClose />
          </ActionIcon>
        </Group>
      </Group>
    </Stack>,
    footerRef.current
  );
};

export default BackgroundPlayer;
