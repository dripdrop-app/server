import { useEffect, useMemo, useRef, useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Card, CardMedia, CardContent, Typography, Link, Stack, Box, useTheme, useMediaQuery } from '@mui/material';
import { YoutubeVideoQueueButton, YoutubeVideoWatchButton } from './YoutubeVideoButtons';

interface VideoCardProps {
	video: YoutubeVideo;
}

const VideoCard = (props: VideoCardProps) => {
	const { video } = props;
	const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });

	const cardImageRef = useRef<HTMLImageElement>(null);

	const theme = useTheme();
	const isSmall = useMediaQuery(theme.breakpoints.down('md'));

	useEffect(() => {
		const cardImage = cardImageRef.current;
		const observer = new ResizeObserver((entries) => {
			for (const entry of entries) {
				const rect = entry.target.getBoundingClientRect();
				setImageDimensions({
					width: rect.width,
					height: rect.height,
				});
			}
		});
		if (cardImage) {
			observer.observe(cardImage);
		}
		return () => {
			if (cardImage) {
				observer.unobserve(cardImage);
			}
		};
	}, [isSmall]);

	return useMemo(() => {
		const publishedAt = new Date(video.publishedAt).toLocaleDateString();
		const channelLink = `/youtube/channel/${video.channelId}`;
		const videoLink = `/youtube/video/${video.id}`;

		return (
			<Card>
				<Stack direction="column" position="relative">
					<CardMedia ref={cardImageRef} component="img" image={video.thumbnail} loading="lazy" />
					<Link component={RouterLink} to={videoLink} sx={{ position: 'absolute' }}>
						<Box
							sx={{ background: 'linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0))' }}
							height={imageDimensions.height}
							width={imageDimensions.width}
						/>
					</Link>
					<Box position="absolute" width="100%" alignItems="center" padding={2}>
						<Box sx={{ float: 'left' }}>
							<YoutubeVideoWatchButton video={video} />
						</Box>
						<Box sx={{ float: 'right' }}>
							<YoutubeVideoQueueButton video={video} />
						</Box>
					</Box>
				</Stack>
				<CardContent component={Stack} direction="column" spacing={2}>
					<Typography variant="body1">
						<Link component={RouterLink} to={videoLink}>
							{video.title}
						</Link>
					</Typography>
					<Stack direction="row" spacing={2} flexWrap="wrap">
						<Typography variant="caption">
							<Link component={RouterLink} to={channelLink}>
								{video.channelTitle}
							</Link>
						</Typography>
						<Typography variant="caption">{publishedAt}</Typography>
					</Stack>
				</CardContent>
			</Card>
		);
	}, [imageDimensions.height, imageDimensions.width, video]);
};

export default VideoCard;
