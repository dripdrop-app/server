import React, { useEffect, useState } from 'react';
import { useRecoilValueLoadable } from 'recoil';
import { Button, CircularProgress, Stack, Tab, Tabs, Typography, Box } from '@mui/material';
import { authAtom } from '../atoms/YoutubeCollections';
import useLazyFetch from '../hooks/useLazyFetch';
import VideosView from '../components/YoutubeCollections/VideosView';
import SubscriptionsView from '../components/YoutubeCollections/SubscriptionsView';

const YoutubeCollections = () => {
	const youtubeEmail = useRecoilValueLoadable(authAtom);
	const [tabIndex, setTabIndex] = useState(0);

	const [getOAuthLink, getOAuthLinkStatus] = useLazyFetch<string>();

	useEffect(() => {
		if (getOAuthLinkStatus.isSuccess) {
			const oAuthURL = getOAuthLinkStatus.data;
			window.location.href = oAuthURL;
		}
	}, [getOAuthLinkStatus]);

	if (youtubeEmail.state === 'loading' || youtubeEmail.state === 'hasError') {
		return (
			<Stack direction="row" justifyContent="center" sx={{ m: 5 }}>
				<CircularProgress />
			</Stack>
		);
	}

	const { email } = youtubeEmail.getValue();

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
						{getOAuthLinkStatus.isLoading ? <CircularProgress /> : 'Log in with Google'}
					</Button>
				</Stack>
			) : (
				<React.Fragment>
					<Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
						<Tabs value={tabIndex} onChange={(e, v) => setTabIndex(v)}>
							<Tab value={0} label="videos" />
							<Tab value={1} label="subscriptions" />
						</Tabs>
					</Box>
					{tabIndex === 0 ? <VideosView channelID={null} /> : null}
					{tabIndex === 1 ? <SubscriptionsView /> : null}
				</React.Fragment>
			)}
		</Stack>
	);
};

export default YoutubeCollections;
