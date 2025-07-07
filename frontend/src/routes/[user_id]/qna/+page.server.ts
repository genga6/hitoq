// import type { PageServerLoad } from './$types';
// import { API_BASE_URL } from '$env/static/private';
// import { error } from '@sveltejs/kit';
// import { qaTemplates } from '$lib/qa-templates'; 

// export const load: PageServerLoad = async ({ fetch, cookies }) => {
//   const authToken = cookies.get('auth_token');
//   if (!authToken) {
//     throw error(401, 'Authentication required');
//   }

//   const response = await fetch(`${API_BASE_URL}/me/qa-answers`, {
//     headers: {
//       'Authorization': `Bearer ${authToken}`
//     }
//   });

//   if (!response.ok) {
//     throw error(response.status, 'Failed to load your Q&A answers.');
//   }

//   const userAnswerGroups = await response.json();
//   const answeredTemplateIds = userAnswerGroups.map(group => group.templateId);
//   const availableTemplates = qaTemplates.filter(
//     template => !answeredTemplateIds.includes(template.id)
//   );

//   return {
//     userAnswerGroups,
//     availableTemplates
//   };
// };