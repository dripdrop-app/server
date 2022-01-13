import React, { useEffect, useState } from 'react';
import { DefaultValue, useRecoilState } from 'recoil';
import { Button, CircularProgress, Stack, Tab, Tabs, Typography, Box } from '@mui/material';
import useLazyFetch from '../hooks/useLazyFetch';
import VideosView from '../components/YoutubeCollections/VideosView';
import SubscriptionsView from '../components/YoutubeCollections/SubscriptionsView';
import { authAtom } from '../atoms/YoutubeCollections';

const YoutubeCollections = () => {
	const [youtubeAuth, setYoutubeAuth] = useRecoilState(authAtom);
	const [tabIndex, setTabIndex] = useState(0);

	const [getOAuthLink, getOAuthLinkStatus] = useLazyFetch<string>();
	const [getYoutubeAccount, getYoutubeAccountStatus] = useLazyFetch<YoutubeState>();

	useEffect(() => {
		if (getOAuthLinkStatus.isSuccess) {
			const oAuthURL = getOAuthLinkStatus.data;
			window.location.href = oAuthURL;
		}
	}, [getOAuthLinkStatus]);

	useEffect(() => {
		if (!youtubeAuth.loaded) {
			getYoutubeAccount({ url: '/youtube/account' });
		}
	}, [getYoutubeAccount, youtubeAuth]);

	useEffect(() => {
		if (getYoutubeAccountStatus.isSuccess) {
			const youtubeAccount = getYoutubeAccountStatus.data;
			setYoutubeAuth((prev) => ({ ...youtubeAccount, loaded: true }));
		}
	}, [getYoutubeAccountStatus.data, getYoutubeAccountStatus.isSuccess, setYoutubeAuth]);

	if (getYoutubeAccountStatus.isLoading) {
		return (
			<Stack direction="row" justifyContent="center" sx={{ m: 5 }}>
				<CircularProgress />
			</Stack>
		);
	}

	return (
		<Stack sx={{ m: 5 }}>
			<Typography sx={{ my: 1 }} variant="h2">
				Youtube Collections
			</Typography>
			{youtubeAuth instanceof DefaultValue || !youtubeAuth.email || youtubeAuth.refresh ? (
				<Stack alignItems="center" margin={10}>
					<Button
						disabled={getOAuthLinkStatus.isLoading}
						variant="contained"
						onClick={() => getOAuthLink({ url: '/youtube/oauth' })}
					>
						{getOAuthLinkStatus.isLoading ? (
							<CircularProgress />
						) : youtubeAuth.refresh ? (
							'Reconnect Google Account'
						) : (
							'Log in with Google'
						)}
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
