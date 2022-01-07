import React from 'react';
import { useRecoilState } from 'recoil';
import { Card, CardMedia, CardContent, Typography, Container, Stack, Link } from '@mui/material';
import { videosAtom } from '../../atoms/YoutubeCollections';
import FiltersView from './FiltersView';
import CustomGrid from './CustomGrid';

const VideosView = (props: { channelID: string | null }) => {
	const [videosView, setVideosView] = useRecoilState(videosAtom(props.channelID));
	const { videos } = videosView;

	return (
		<Container sx={{ my: 5 }}>
			<FiltersView state={videosView} updateState={setVideosView}>
				<CustomGrid
					items={videos}
					renderItem={(video) => {
						const publishedAt = new Date(video.published_at).toLocaleDateString();
						return (
							<Card sx={{ height: '100%' }}>
								<Stack sx={{ height: '100%' }} flexDirection="column" direction="column">
									<Link sx={{ flex: 2 }} target="_blank" href={`https://youtube.com/watch?v=${video.id}`}>
										<CardMedia component="img" image={video.thumbnail} />
									</Link>
									<CardContent sx={{ flex: 1 }}>
										<Typography variant="subtitle1">
											<Link
												sx={{ textDecoration: 'none' }}
												target="_blank"
												href={`https://youtube.com/watch?v=${video.id}`}
											>
												{video.title}
											</Link>
										</Typography>
									</CardContent>
									<CardContent>
										<Stack direction="row" justifyContent="space-between" flexWrap="wrap" spacing={1}>
											<Typography variant="caption">
												<Link
													sx={{ textDecoration: 'none' }}
													target="_blank"
													href={`https://youtube.com/channel/${video.channel_id}`}
												>
													{video.channel_title}
												</Link>
											</Typography>
											<Typography variant="caption">{publishedAt}</Typography>
										</Stack>
									</CardContent>
								</Stack>
							</Card>
						);
					}}
				/>
			</FiltersView>
		</Container>
	);
};

export default VideosView;
