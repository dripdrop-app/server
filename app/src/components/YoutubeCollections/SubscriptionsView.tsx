import React from 'react';
import { Container, Pagination, Skeleton, Stack, ToggleButton, ToggleButtonGroup } from '@mui/material';
import { useRecoilState, useRecoilValueLoadable } from 'recoil';
import CustomGrid from './CustomGrid';
import YoutubeSubscriptionCard from './YoutubeSubscriptionCard';
import { subscriptionOptionsState, subscriptionsSelector } from '../../state/YoutubeCollections';

const PerPageSelector = () => {
	const [subscriptionOptions, updateSubscriptionOptions] = useRecoilState(subscriptionOptionsState);
	const { perPage } = subscriptionOptions;

	return (
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
	);
};

const SubscriptionsDisplay = () => {
	const [subscriptionOptions, updateSubscriptionOptions] = useRecoilState(subscriptionOptionsState);
	const subscriptionsState = useRecoilValueLoadable(subscriptionsSelector);
	const { perPage, page } = subscriptionOptions;

	if (subscriptionsState.state === 'loading' || subscriptionsState.state === 'hasError') {
		return (
			<Stack justifyContent="center" direction="row" sx={{ my: 5 }}>
				<CustomGrid
					items={Array(perPage).fill(0)}
					renderItem={(i, selected) => <Skeleton width="100%" height="10em" variant="rectangular" />}
				/>
			</Stack>
		);
	}

	const { subscriptions, totalSubscriptions } = subscriptionsState.contents;

	return (
		<React.Fragment>
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
		</React.Fragment>
	);
};

const SubscriptionsView = () => {
	return (
		<React.Fragment>
			<Container sx={{ my: 5 }}>
				<Stack sx={{ my: 2 }} direction="row" justifyContent="flex-end">
					<PerPageSelector />
				</Stack>
				<SubscriptionsDisplay />
			</Container>
		</React.Fragment>
	);
};

export default SubscriptionsView;
