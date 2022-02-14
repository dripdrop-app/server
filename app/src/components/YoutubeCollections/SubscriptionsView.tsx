import React from 'react';
import { CircularProgress, Container, Pagination, Stack, ToggleButton, ToggleButtonGroup } from '@mui/material';
import { useRecoilState, useRecoilValueLoadable } from 'recoil';
import CustomGrid from './CustomGrid';
import YoutubeSubscriptionCard from './YoutubeSubscriptionCard';
import { subscriptionOptionsState, subscriptionsSelector } from '../../state/YoutubeCollections';

const SubscriptionsView = () => {
	const [subscriptionOptions, updateSubscriptionOptions] = useRecoilState(subscriptionOptionsState);
	const subscriptionsState = useRecoilValueLoadable(subscriptionsSelector);

	if (subscriptionsState.state === 'loading' || subscriptionsState.state === 'hasError') {
		return (
			<Stack justifyContent="center" direction="row" sx={{ my: 5 }}>
				<CircularProgress />
			</Stack>
		);
	}

	const { subscriptions, totalSubscriptions } = subscriptionsState.contents;
	const { perPage, page } = subscriptionOptions;

	return (
		<React.Fragment>
			<Container sx={{ my: 5 }}>
				<Stack sx={{ my: 2 }} direction="row" justifyContent="flex-end">
					<ToggleButtonGroup
						exclusive
						value={perPage}
						onChange={(e, v) => updateSubscriptionOptions({ ...subscriptionOptions, perPage: v })}
					>
						{([10, 25, 50] as PageState['perPage'][]).map((v) => (
							<ToggleButton key={v} value={v}>
								{v}
							</ToggleButton>
						))}
					</ToggleButtonGroup>
				</Stack>
				<CustomGrid
					items={subscriptions}
					renderItem={(subscription, selected) => (
						<YoutubeSubscriptionCard subscription={subscription} selected={selected} showChannelVideos={(s) => {}} />
					)}
				/>
				<Stack direction="row" sx={{ my: 5 }} justifyContent="center">
					<Pagination
						page={page}
						onChange={(e, page) => updateSubscriptionOptions({ ...subscriptionOptions, page })}
						count={Math.ceil(totalSubscriptions / perPage)}
						color="primary"
					/>
				</Stack>
			</Container>
		</React.Fragment>
	);
};

export default SubscriptionsView;
