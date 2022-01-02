import React, { useEffect } from 'react';
import { useRecoilValueLoadable } from 'recoil';
import { Button, CircularProgress, Stack, Typography } from '@mui/material';
import { youtubeAuthAtom } from '../atoms/YoutubeCollections';
import useLazyFetch from '../hooks/useLazyFetch';

const YoutubeCollections = () => {
	const youtubeEmail = useRecoilValueLoadable(youtubeAuthAtom);

	const [getOAuthLink, getOAuthLinkStatus] = useLazyFetch();

	let pageDisplay = null;

	if (youtubeEmail.state === 'loading') {
		pageDisplay = (
			<Stack alignItems="center" margin={10}>
				<CircularProgress />
			</Stack>
		);
	} else if (youtubeEmail.state === 'hasValue') {
		if (!youtubeEmail.getValue()) {
			pageDisplay = (
				<Stack alignItems="center" margin={10}>
					<Button
						disabled={getOAuthLinkStatus.isLoading}
						variant="contained"
						onClick={() => getOAuthLink({ url: '/youtube/oauth' })}
					>
						{getOAuthLinkStatus.isLoading ? <CircularProgress /> : 'Log in with Google'}
					</Button>
				</Stack>
			);
		}
	}

	useEffect(() => {
		if (getOAuthLinkStatus.isSuccess) {
			const oAuthURL = getOAuthLinkStatus.data;
			window.location.href = oAuthURL;
		}
	}, [getOAuthLinkStatus]);

	return (
		<Stack sx={{ m: 5 }}>
			<Typography variant="h2">Youtube Collections</Typography>
			{pageDisplay}
		</Stack>
	);
};

export default YoutubeCollections;
