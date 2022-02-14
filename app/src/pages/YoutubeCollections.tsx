import React, { useEffect } from 'react';
import { useRecoilValueLoadable } from 'recoil';
import { Button, CircularProgress, Divider, Stack, Typography } from '@mui/material';
import useLazyFetch from '../hooks/useLazyFetch';
import VideosView from '../components/YoutubeCollections/VideosView';
import SubscriptionsView from '../components/YoutubeCollections/SubscriptionsView';
import { authSelector } from '../state/YoutubeCollections';

interface YoutubeCollectionsProps {
	page: 'VIDEOS' | 'SUBSCRIPTIONS';
}

const YoutubeCollections = (props: YoutubeCollectionsProps) => {
	const youtubeAuth = useRecoilValueLoadable(authSelector);

	const [getOAuthLink, getOAuthLinkStatus] = useLazyFetch<string>();

	useEffect(() => {
		if (getOAuthLinkStatus.isSuccess) {
			const oAuthURL = getOAuthLinkStatus.data;
			window.location.href = oAuthURL;
		}
	}, [getOAuthLinkStatus]);

	if (youtubeAuth.state === 'loading' || youtubeAuth.state === 'hasError') {
		return (
			<Stack direction="row" justifyContent="center" sx={{ m: 5 }}>
				<CircularProgress />
			</Stack>
		);
	}

	const { email, refresh } = youtubeAuth.contents;

	return (
		<Stack sx={{ m: 5 }}>
			<Typography sx={{ my: 1 }} variant="h2">
				Youtube Collections
			</Typography>
			{!email ? (
				<Stack alignItems="center" margin={10}>
					<Button
						disabled={getOAuthLinkStatus.isLoading}
						variant="contained"
						onClick={() => getOAuthLink({ url: '/youtube/oauth' })}
					>
						{getOAuthLinkStatus.isLoading ? (
							<CircularProgress />
						) : refresh ? (
							'Reconnect Google Account'
						) : (
							'Log in with Google'
						)}
					</Button>
				</Stack>
			) : (
				<React.Fragment>
					<Typography sx={{ m: 1 }} variant="h5">
						{props.page.charAt(0).toLocaleUpperCase() + props.page.substring(1).toLocaleLowerCase()}
					</Typography>
					<Divider />
					{props.page === 'VIDEOS' ? <VideosView channelID={null} /> : null}
					{props.page === 'SUBSCRIPTIONS' ? <SubscriptionsView /> : null}
				</React.Fragment>
			)}
		</Stack>
	);
};

export default YoutubeCollections;
