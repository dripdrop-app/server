import React, { useMemo } from 'react';
import { Card, Stack, CardMedia, CardContent, Typography } from '@mui/material';
import CustomLink from '../Link';

interface YoutubeVideoCardProps {
	selected: boolean;
	video: YoutubeVideo;
}

const YoutubeVideoCard = (props: YoutubeVideoCardProps) => {
	const video = props.video;
	const publishedAt = new Date(video.published_at).toLocaleDateString();
	const videoLink = `https://youtube.com/watch?v=${video.id}`;
	const channelLink = `https://youtube.com/channel/${video.channel_id}`;

	return useMemo(
		() => (
			<Card sx={{ height: '100%' }} raised={props.selected}>
				<Stack sx={{ height: '100%' }} flexDirection="column" direction="column">
					<CustomLink
						href={videoLink}
						text={<CardMedia sx={{ border: 0, flex: 2 }} component="img" image={video.thumbnail} />}
					/>
					<CardContent sx={{ flex: 1 }}>
						<Typography variant="subtitle1">
							<CustomLink useMaterial={true} href={videoLink} text={video.title} />
						</Typography>
					</CardContent>
					<CardContent>
						<Stack direction="row" justifyContent="space-between" flexWrap="wrap" spacing={1}>
							<Typography variant="caption">
								<CustomLink useMaterial={true} href={channelLink} text={video.channel_title} />
							</Typography>
							<Typography variant="caption">{publishedAt}</Typography>
						</Stack>
					</CardContent>
				</Stack>
			</Card>
		),
		[channelLink, props.selected, publishedAt, video.channel_title, video.thumbnail, video.title, videoLink]
	);
};

export default YoutubeVideoCard;
